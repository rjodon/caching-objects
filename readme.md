# Cached objects

Just a prototype of time expiracy based cache using `OrderedDict`. 

- If an item of the dict is get, we update its expiracy time.
- If not, we delete the item after expiracy.
- A scheduled timer is running in a concurent thread to live monitor the expiracy of each item

## Todo

- See if I could make a version with a binary tree
- Replace the use of built-in `sorted` with a clever insert mechanism (using dichotomy for instance) 
