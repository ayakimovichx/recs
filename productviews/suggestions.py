from .models import View, Product
from django.contrib.auth.models import User
import numpy as np
import pandas as pd
import scipy.sparse
from sklearn.preprocessing import MinMaxScaler
import random
import implicit

def make_train(ratings, pct_test = 0.2):
    '''
    This function will take in the original user-item matrix and "mask" a percentage of the original ratings where a
    user-item interaction has taken place for use as a test set. The test set will contain all of the original ratings, 
    while the training set replaces the specified percentage of them with a zero in the original ratings matrix. 
    
    parameters: 
    
    ratings - the original ratings matrix from which you want to generate a train/test set. Test is just a complete
    copy of the original set. This is in the form of a sparse csr_matrix. 
    
    pct_test - The percentage of user-item interactions where an interaction took place that you want to mask in the 
    training set for later comparison to the test set, which contains all of the original ratings. 
    
    returns:
    
    training_set - The altered version of the original data with a certain percentage of the user-item pairs 
    that originally had interaction set back to zero.
    
    test_set - A copy of the original ratings matrix, unaltered, so it can be used to see how the rank order 
    compares with the actual interactions.
    
    user_inds - From the randomly selected user-item indices, which user rows were altered in the training data.
    This will be necessary later when evaluating the performance via AUC.
    '''
    test_set = ratings.copy() # Make a copy of the original set to be the test set. 
    test_set[test_set != 0] = 1 # Store the test set as a binary preference matrix
    training_set = ratings.copy() # Make a copy of the original data we can alter as our training set. 
    nonzero_inds = training_set.nonzero() # Find the indices in the ratings data where an interaction exists
    nonzero_pairs = list(zip(nonzero_inds[0], nonzero_inds[1])) # Zip these pairs together of user,item index into list
    random.seed(0) # Set the random seed to zero for reproducibility
    num_samples = int(np.ceil(pct_test*len(nonzero_pairs))) # Round the number of samples needed to the nearest integer
    samples = random.sample(nonzero_pairs, num_samples) # Sample a random number of user-item pairs without replacement
    user_inds = [index[0] for index in samples] # Get the user row indices
    item_inds = [index[1] for index in samples] # Get the item column indices
    training_set[user_inds, item_inds] = 0 # Assign all of the randomly chosen user-item pairs to zero
    training_set.eliminate_zeros() # Get rid of zeros in sparse array storage after update to save space
    return training_set, test_set, list(set(user_inds)) # Output the unique list of user rows that were altered  


def get_items_viewed(customer_id, mf_train, customers_list, products_list, item_lookup):
    '''
    This just tells me which items have been already purchased by a specific user in the training set. 
    
    parameters: 
    
    customer_id - Input the customer's id number that you want to see prior purchases of at least once
    
    mf_train - The initial ratings training set used (without weights applied)
    
    customers_list - The array of customers used in the ratings matrix
    
    products_list - The array of products used in the ratings matrix
    
    item_lookup - A simple pandas dataframe of the unique product ID/product descriptions available
    
    returns:
    
    A list of item IDs and item descriptions for a particular customer that were already purchased in the training set
    '''
    cust_ind = np.where(customers_list == customer_id)[0][0] # Returns the index row of our customer id
    viewed_ind = mf_train[cust_ind,:].nonzero()[1] # Get column indices of purchased items
    prod_codes = products_list[viewed_ind] # Get the stock codes for our purchased items
    return item_lookup.loc[item_lookup.itemid.isin(prod_codes)]


def rec_items(customer_id, mf_train, user_vecs, item_vecs, customer_list, item_list, item_lookup, num_items = 10):
    '''
    This function will return the top recommended items to our users 
    
    parameters:
    
    customer_id - Input the customer's id number that you want to get recommendations for
    
    mf_train - The training matrix you used for matrix factorization fitting
    
    user_vecs - the user vectors from your fitted matrix factorization
    
    item_vecs - the item vectors from your fitted matrix factorization
    
    customer_list - an array of the customer's ID numbers that make up the rows of your ratings matrix 
                    (in order of matrix)
    
    item_list - an array of the products that make up the columns of your ratings matrix
                    (in order of matrix)
    
    item_lookup - A simple pandas dataframe of the unique product ID/product descriptions available
    
    num_items - The number of items you want to recommend in order of best recommendations. Default is 10. 
    
    returns:
    
    - The top n recommendations chosen based on the user/item vectors for items never interacted with/purchased
    '''
    
    cust_ind = np.where(customer_list == customer_id)[0][0] # Returns the index row of our customer id
    pref_vec = mf_train[cust_ind,:].toarray() # Get the ratings from the training set ratings matrix
    pref_vec = pref_vec.reshape(-1) + 1 # Add 1 to everything, so that items not purchased yet become equal to 1
    pref_vec[pref_vec > 1] = 0 # Make everything already purchased zero
    rec_vector = user_vecs[cust_ind,:].dot(item_vecs.T) # Get dot product of user vector and all item vectors
    # Scale this recommendation vector between 0 and 1
    min_max = MinMaxScaler()
    rec_vector_scaled = min_max.fit_transform(rec_vector.reshape(-1,1))[:,0] 
    recommend_vector = pref_vec*rec_vector_scaled 
    # Items already purchased have their recommendation multiplied by zero
    product_idx = np.argsort(recommend_vector)[::-1][:num_items] # Sort the indices of the items into order 
    # of best recommendations
    rec_list = [] # start empty list to store items
    for index in product_idx:
        code = item_list[index]
        rec_list.append([code, item_lookup.itemname.loc[item_lookup.itemid == code].iloc[0]]) 
        # Append our descriptions to the list
    codes = [item[0] for item in rec_list]
    descriptions = [item[1] for item in rec_list]
    final_frame = pd.DataFrame({'User ID':cust_ind, 'Item ID': codes, 'Description': descriptions}) # Create a dataframe 
    return final_frame[['User ID', 'Item ID', 'Description']] # Switch order of columns around


def update_recs():
    num_views = View.objects.count()
    update_step = ((num_views/100)+1) * 5
    
    if num_views % update_step == 0:
        # Create sparse matrix
        grouped_views = pd.read_csv('data\views_grouped_id.csv') # ! TEST - data should be sourced from DB or transformed CSV file
        visitors = list(np.sort(grouped_views.visitorid.unique())) # Get our unique visitors
        products = list(grouped_views.nuitemid.unique()) # Get our unique products/items
        viewcount = list(grouped_views.event) # all of our visits
        
        visitors_count = len(visitors)
        
        rows = grouped_views.visitorid.astype('category', categories = visitors).cat.codes # Get the associated row indices
        cols = grouped_views.nuitemid.astype('category', categories = products).cat.codes # Get the associated column indices
        visits_sparse = scipy.sparse.csr_matrix((viewcount, (rows, cols)), shape=(len(visitors), len(products)))
        
        # matrix_size = visits_sparse.shape[0]*visits_sparse.shape[1] # Number of possible interactions in the matrix
        # num_visits = len(visits_sparse.nonzero()[0]) # Number of items interacted with
        # sparsity = 100*(1 - (num_visits/matrix_size))
        # sparsity
        
        # train/test split
        product_train, product_test, product_users_altered = make_train(visits_sparse, pct_test = 0.2)
        
        # ALS 
        alpha = 15
        user_vecs, item_vecs = implicit.alternating_least_squares((product_train*alpha).astype('double'), 
                                                          factors=20, 
                                                          regularization = 0.1, 
                                                         iterations = 50)
        
        # preprocess for recs generation
        
        visitors_arr = np.array(visitors)
        products_arr = np.array(products)
        # read list of products with categories
        items = pd.read_csv('data\jj_product.csv')
        
        # generate recs for users
        
        for visitor in visitors:
            rec_items (visitor, product_train, user_vecs, item_vecs, visitors_arr, products_arr, items, num_items = 10)

def run_user_recs():
    # test 
    items = pd.read_csv('c:\jjrecs\productviews\data\jj_product.csv')
    visitors_arr = np.fromfile('c:\jjrecs\productviews\data\rs_visitors_arr.dat', dtype=int, sep=',')
    products_arr = np.fromfile('c:\jjrecs\productviews\data\rs_products_arr.dat', dtype=int, sep=',')
    users_vecs = np.fromfile('c:\jjrecs\productviews\data\rs_user_vecs.dat', dtype=float, sep=',').reshape(1404179,20)
    items_vecs = np.fromfile('c:\jjrecs\productviews\data\rs_item_vecs.dat', dtype=float, sep=',').reshape(137,20)
    product_train = scipy.sparse.load_npz('c:\jjrecs\productviews\data\rs_product_train.npz')
    # generate recs for user
    rec_items (user_name_current, product_train, user_vecs, item_vecs, visitors_arr, products_arr, items, num_items = 10)
