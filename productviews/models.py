from django.db import models
import numpy as np


class Product(models.Model):
    name = models.CharField(max_length=200)
    
    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        return np.mean(all_ratings)
        
    def __unicode__(self):
        return self.name


class View(models.Model):
    VIEW_FLAGS = (
        (0, '0'),
		(1, '1')
    )
    product = models.ForeignKey(Product)
    pub_date = models.DateTimeField('date viewed')
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=VIEW_FLAGS)