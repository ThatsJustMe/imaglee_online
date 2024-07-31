import graphene
from graphene_django.types import DjangoObjectType  # Automatically generates GraphQL types from Django models
from django.db import models
from django.apps import apps


# List of models and corresponding types
#
	models = {}


# Dynamically adds models from all apps
#
	for app_config in apps.get_app_configs():
		for model in app_config.get_models():
			models[model.__name__] = model


# Dynamically creates DjangoObjectType for each model in models variable
#
	for model_name, model in models.items():
		meta_class = type('Meta', (), {'model': model})
		model_type = type(f'{model_name}Type', (DjangoObjectType,), {'Meta': meta_class})
		globals()[f'{model_name}Type'] = model_type


# Query class definitions
#
	class Query(graphene.ObjectType):
		pass


# Dynamically adds fields and resolvers into Query class defined above
#
	for model_name, model in models.items():
		singular_name = model_name.lower()
		plural_name = f'all_{singular_name}s'
		
		setattr(Query, singular_name, graphene.Field(globals()[f'{model_name}Type'], id=graphene.Int(required=True)))
		setattr(Query, plural_name, graphene.List(globals()[f'{model_name}Type']))
	
		def resolve_singular(self, info, id, model=model):
			try:
				return model.objects.get(pk=id)
			except model.DoesNotExist:
				return None
	
		def resolve_plural(self, info, model=model):
			return model.objects.all()
		
		setattr(Query, f'resolve_{singular_name}', resolve_singular)
		setattr(Query, f'resolve_{plural_name}', resolve_plural)


# Mutation class definition
#
	class Mutation(graphene.ObjectType):
		pass


# Dynamically creates mutations from Mutation class, for all fields given model could possibly have
#
	def create_mutation_class(model_name, model):
		class CreateModelMutation(graphene.Mutation):
			class Arguments:
				# Dynamically creates argument for each field in the model
				for field in model._meta.fields:
					if isinstance(field, models.CharField):
						field_type = graphene.String
					elif isinstance(field, models.IntegerField):
						field_type = graphene.Int
					elif isinstance(field, models.BooleanField):
						field_type = graphene.Boolean
					elif isinstance(field, models.DateField):
						field_type = graphene.Date
					elif isinstance(field, models.DateTimeField):
						field_type = graphene.DateTime
					elif isinstance(field, models.FloatField):
						field_type = graphene.Float
					else:
						continue  # And ignores the fields that are not supported
					locals()[field.name] = field_type(required=not field.blank)
			
			model_instance = graphene.Field(globals()[f'{model_name}Type'])
	
			# Creates and returns CreateModelMutation instance, i.e. when there is GraphQL query this instance will take care of returning the data from DB
			def mutate(self, info, **kwargs):
				model_instance = model(**kwargs)
				model_instance.save()
				return CreateModelMutation(model_instance=model_instance)
		
		return CreateModelMutation


# Dynamically adds mutations into Mutation class defined above
#
	for model_name, model in models.items():
		mutation_class = create_mutation_class(model_name, model)
		mutation_field_name = f'create_{model_name.lower()}'
		setattr(Mutation, mutation_field_name, mutation_class.Field())


# Exports schema
#
	schema = graphene.Schema(query=Query, mutation=Mutation)
