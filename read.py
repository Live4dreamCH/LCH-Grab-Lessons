import pickle
with open('Caches.data', 'rb') as f:
    pickle.load(f)
    courses = pickle.load(f)
    print(courses)