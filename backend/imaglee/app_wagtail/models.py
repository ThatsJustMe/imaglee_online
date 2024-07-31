from django.db import models
from django.urls import reverse

from wagtail.images.models import AbstractImage, AbstractRendition
from wagtail.images import get_image_model_string
from wagtail.admin.edit_handlers import FieldPanel


# Extends Wagtail's AbstractImage to customize how image renditions are generated, ensuring that they use protected URLs requiring user authentication
#
	class CustomImage(AbstractImage):
		admin_form_fields = AbstractImage.admin_form_fields
	
		def get_rendition(self, filter):
			rendition = super().get_rendition(filter)
			protected_url = reverse('protected_media', args=[rendition.file.name])
			rendition.url = protected_url
			
			return rendition


# Extends AbstractRendition to manage different versions of an image
# Ensures uniqueness for each rendition configuration and linking renditions back to their original images
#
	class CustomRendition(AbstractRendition):
		image = models.ForeignKey(CustomImage, related_name='renditions', on_delete=models.CASCADE)
	
		class Meta:
			unique_together = (
				('image', 'filter_spec', 'focal_point_key'),
			)