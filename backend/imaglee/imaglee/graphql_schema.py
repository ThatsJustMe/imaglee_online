import main_schema
import graphene
import graphql_jwt

from graphene_django.types import DjangoObjectType
from django.apps import apps
from graphql_jwt.decorators import login_required


# Reads Docker Secrets
#
	def read_secret(secret_name):
		with open(f"/run/secrets/{secret_name}") as secret_file:
			return secret_file.read().strip()


# Class that dynamically creates GraphQL Types, Queries, and Mutations
#
	class DynamicTypeGenerator:
		def __init__(self):
			self.query_classes = {}
			self.mutation_classes = {}
	
		# Creates GraphQL Type class for a given model
		def create_graphql_type(self, model):
			class Meta:
				model = model
			return type(f'{model.__name__}Type', (DjangoObjectType,), {'Meta': Meta})
	
		# Creates Query class for a given model
		def create_query_class(self, model, graphql_type):
			singular_name = model._meta.model_name.lower()
			plural_name = f'all_{singular_name}s'
	
			class Query(graphene.ObjectType):
				model_name_singular = graphene.Field(graphql_type, id=graphene.Int(required=True))
				model_name_plural = graphene.List(graphene.NonNull(graphql_type))
	
				@login_required
				def resolve_model_name_singular(self, info, id):
					try:
						return model.objects.get(pk=id)
					except model.DoesNotExist:
						return None
	
				@login_required
				def resolve_model_name_plural(self, info):
					return model.objects.all()
	
			return type(f'{model.__name__}Query', (Query,), {
				singular_name: graphene.Field(graphql_type, id=graphene.Int(required=True)),
				plural_name: graphene.List(graphene.NonNull(graphql_type)),
				f'resolve_{singular_name}': Query.resolve_model_name_singular,
				f'resolve_{plural_name}': Query.resolve_model_name_plural
			})


	# Creates Mutation class for a given model
	def create_mutation_class(self, model, graphql_type):
		class CreateModel(graphene.Mutation):
			class Arguments:
				# Dynamické vytváření argumentů pro každé pole v modelu
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
						continue  # Ignorovat pole, která nejsou podporována
					locals()[field.name] = field_type(required=not field.blank)

			model_instance = graphene.Field(graphene.NonNull(graphql_type))

			@login_required
			def mutate(self, info, **kwargs):
				model_instance = model.objects.using(self.get_db_name(model)).create(**kwargs)
				return CreateModel(model_instance=model_instance)

		return type(f'Create{model.__name__}Mutation', (graphene.ObjectType,), {'create_model': CreateModel.Field()})

	# Gets DB name based on the app name
	def get_db_name(self, model):
		app_label = model._meta.app_label
		if app_label in ['app_wagtail']:
			return 'db_wagtail'
		elif app_label in ['auth', 'admin', 'sessions', 'contenttypes', 'sites', 'flatpages', 'redirects', 'logentry']:
			return 'db_django'
		else:
			return 'db_apps'

	# Generates Types, Queries and Mutation classes for all models
	def generate(self):
		for model in apps.get_models():
			graphql_type = self.create_graphql_type(model)
			query_class = self.create_query_class(model, graphql_type)
			mutation_class = self.create_mutation_class(model, graphql_type)
			
			self.query_classes[model._meta.model_name] = query_class
			self.mutation_classes[model._meta.model_name] = mutation_class


# Runs the dynamic generation of Types, Queries and Mutation classes for all models
#
	generator = DynamicTypeGenerator()
	generator.generate()

# AuthMutation class for authentication-related mutations
#
	class AuthMutation(graphene.ObjectType):
		token_auth = graphql_jwt.ObtainJSONWebToken.Field()
		verify_token = graphql_jwt.Verify.Field()
		refresh_token = graphql_jwt.Refresh.Field()
		revoke_token = graphql_jwt.Revoke.Field()

# Main query and mutation classes
#
	class Query(main_schema.Query, graphene.ObjectType):
		pass


	class Mutation(AuthMutation, main_schema.Mutation, graphene.ObjectType):
		pass


# Adds dynamically generated queries to the main Query class defined above
#
	for query_class in generator.query_classes.values():
		for attr, value in query_class.__dict__.items():
			if not attr.startswith('__'):
				setattr(Query, attr, value)


# Adds dynamically generated mutations to the main Mutation class defined above
#
	for mutation_class in generator.mutation_classes.values():
		for attr, value in mutation_class.__dict__.items():
			if not attr.startswith('__'):
				setattr(Mutation, attr, value)


# Exports schema
#
	schema = graphene.Schema(query=Query, mutation=Mutation)