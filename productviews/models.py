from django.db import models
import numpy as np


class Product(models.Model):
    name = models.CharField(max_length=200)
    
    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.view_set.all())
        return np.sum(all_ratings)
        
    def __unicode__(self):
        return self.name


class View(models.Model):
    product = models.ForeignKey(Product)
    pub_date = models.DateTimeField('date viewed')
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField(default=1)