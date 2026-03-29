from django.db import models


class Property_details(models.Model):
    title= models.CharField(max_length=200)
    price= models.IntegerField()
    rating=models.DecimalField(max_digits=5, decimal_places=2)
    property_type=models.CharField(max_length=50)
    location= models.CharField(max_length=100)
    cost_of_living= models.IntegerField()


    image = models.ImageField(upload_to='property_images/')

    Agent = models.ForeignKey('Agent', on_delete=models.CASCADE)
    property_rooms = models.ForeignKey('Property_rooms', on_delete=models.CASCADE,null=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    

class Agent(models.Model):
    name=models.CharField(max_length=100)
    mail_id=models.EmailField()
    rating = models.DecimalField(max_digits=5, decimal_places=2)
    sold =models.IntegerField()
    reviews= models.IntegerField()

    agent_image = models.ImageField(upload_to='agent_images/', null=True)

    def __str__(self):
        return self.name
    

class Property_rooms(models.Model):
    bedrooms = models.IntegerField(default=1)
    bathroom = models.IntegerField(default=1)
    kitchen = models.IntegerField(default=1)
    store_room = models.IntegerField(default=1)
    balcony = models.IntegerField(default=1)

    def __str__(self):
      return str(self.bedrooms)







