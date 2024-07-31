import os

from django.conf import settings
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required


# Ensures that media files are only accessible to authenticated users using the @login_required decorator
# It constructs the full file path based on the path parameter and the MEDIA_ROOT setting, checks if the file exists, and if so, serves it using a FileResponse # If the file doesn't exist, it raises a 404 error.
#
	@login_required
	def protected_media(request, path):
		file_path = os.path.join(settings.MEDIA_ROOT, path)
		if os.path.exists(file_path):
			return FileResponse(open(file_path, 'rb'))
		else:
			raise Http404("File not found")