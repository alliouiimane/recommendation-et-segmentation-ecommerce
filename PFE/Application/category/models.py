from django.db import models
from django.urls import reverse

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=370, unique=True)
    description = models.TextField(max_length=360)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


    def get_url(self):
        return reverse('product_by_category',args=[self.slug])
    def __str__(self):
        return self.category_name
