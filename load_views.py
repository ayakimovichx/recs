import sys, os 
import pandas as pd
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jjrecs.settings")

import django
django.setup()

from productviews.models import View, Product 


def save_view_from_row(view_row):
    view = View()
    view.id = view_row[0]
    view.user_id = view_row[1]
    view.rating = view_row[2]
    view.product = Product.objects.get(id=view_row[3])
    view.user_name = view_row[5]
    view.pub_date = datetime.datetime.now()
    view.save()
    
    
if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        print "Reading from file " + str(sys.argv[1])
        views_df = pd.read_csv(sys.argv[1])
        print views_df

        views_df.apply(
            save_view_from_row,
            axis=1
        )

        print "There are {} views in DB".format(View.objects.count())
        
    else:
        print "Please, provide Views file path"