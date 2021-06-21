from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.operations import HStoreExtension

#ZInfo Models and objects are visible from pgAdmin4
class ZInfo(models.Model):
    #Consulted django documentation for Model fields
    url = models.CharField(max_length = 120)
    hash = HStoreField(blank=False, null=False)
    date = models.CharField(max_length = 50)
    percent = models.CharField(max_length = 10)
    language = models.CharField(max_length = 10)

    #Reordering the dictionary since it is unordered after taking it from the DB
    #O(2N)
    def getHash(self):
        newHash = self.hash
        #Changing the values back to integers
        newHash = dict((keys, int(values)) for keys, values in newHash.items())
        #Sorting the dictionary by the values (item[1])
        newHash = dict(sorted(newHash.items(), key=lambda item: item[1], reverse=True))
        #Return the new ordered dict
        return newHash

    def __str__(self):
        return self.url
