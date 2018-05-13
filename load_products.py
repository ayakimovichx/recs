import sys, os 
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jjrecs.settings")

import django
django.setup()

from productviews.models import Product 


def save_product_from_row(product_row):
    product = Product()
    product.id = product_row[0]
    product.name = product_row[1]
    product.category = product_row[2]
    product.save()
    
    
if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        print "Reading from file " + str(sys.argv[1])
        products_df = pd.read_csv(sys.argv[1])
        print products_df

        products_df.apply(
            save_product_from_row,
            axis=1
        )

        print "There are {} product items".format(Product.objects.count())
        
    else:
        print "Please, provide Product file path"