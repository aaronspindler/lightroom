from django.db import models
from django.utils.html import mark_safe

class Photo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    image = models.ImageField(upload_to='raw_images')
    
    def image_tag(self):
        return mark_safe('<img src="%s"/>' % (self.image.url))
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True