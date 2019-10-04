#!/usr/bin/python

'''
USE AT YOUR OWN PERIL <3
fill in your API keys before running the script
written in Python3 by Judith van Stegeren, @jd7h
'''

from random import randrange
import time
import json
import twitter #for docs, see https://python-twitter.readthedocs.io/en/latest/twitter.html
import spoonacular as sp

from config import *
# connect to api with apikeys
# if you don't have apikeys, go to apps.twitter.com
api = twitter.Api(consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token_key=access_token,
                    access_token_secret=token_secret)
sp_api = sp.API(spoonacular_key)

# Detect the food mentions in the tweet
def detectFoodInTweet(tweet):
    response = sp_api.detect_food_in_text(tweet)
    data = response.json()
    return data["annotations"]

def getRecipeDetails(json_recipe):
    return [json_recipe[0]['id'], json_recipe[0]['title'], json_recipe[0]['image']]

# Return a recipe depending on the first detected food item
def returnRecipe(food):
    dishes = []
    ingredients = []
    for item in food:
        if item['tag'] == "dish":
            dishes.append(item)
        elif item['tag'] == "ingredient":
            ingredients.append(item['annotation'])
    ingredients_string = ','.join(map(str, ingredients)) 
    print(ingredients_string)

    if len(dishes) > 0:
        print("found a dish!", dishes[0]['annotation'])
        response = sp_api.search_recipes_complex(query = dishes[0]['annotation'], number = 1, includeIngredients = ingredients_string)
        search_result = response.json()
        return getRecipeDetails(search_result['results'])
    elif len(ingredients) > 0:
        response = sp_api.search_recipes_by_ingredients(ingredients = ingredients_string, number = 1)
        search_result = response.json()
        return getRecipeDetails(search_result)
    else:
        response = sp_api.get_random_recipes(number = 1).json()
        search_result = response.json()
        return getRecipeDetails(search_result)

# random dish response
# in my day
# I think it's fantasic, really
# I wrote this recipe on paper, let me see. Ah yes, I got it
# Super isn't it, really marvellous
# deary me

#make haste and start now!

def grandmaSentences(number):

    sentences = [
    ['header', 'Hello dear', 'Hello lovely' , 'Hello my dear,', 'Thanks for your message',],
    ['randomReason',
         'Hello?... My hearing aid is not working properly. ', 'Oops... deary me! I forgot my reading glasses.', 
         'Yeah sorry... Didn\'t know you were talking to me. ', 'Back in my day, we did not use those ingredients. '],
    ['randomIngredients', 'Could you repeat those ingredients for me darling?', 'What ingredients did you mention dear?',
    'It would be marvellous if you can tell me those ingredients again, darling. Just one more time.'],    
    ['closure', 'Tell me if you liked it!', 'Enjoy cooking!', 'Granny out.', 'Have a nice meal!', 'Bon Appetite!',
     'Make haste and start now, so you can enjoy your marvellous meal sweetheart.'], 
    ['foundrecipe', 'Granny recommends ', 'I would make ', 'You should try the ', 'You should definitely cook ', 'I wrote this one on paper, let me see. Ah '],
    ]
    return sentences[number][randrange(1, len(sentences[number]))]

def createResponse(title):
    response = ""
    header = grandmaSentences(0)
    foundRecipe = grandmaSentences(4)
    closure = grandmaSentences(3)
    response = header + "\n" + foundRecipe + title + "\n" + closure
    return response

def createRandomResponse(user):
    response = ""
    randomIngredients = grandmaSentences(2)
    randomReason = grandmaSentences(1)
    response = user + " " + randomReason + '\n' + randomIngredients
    return response

def tweetResponse(response, tweet_id):
    print("Posting reply...")
    print("tweet id ", tweet_id)
    print(response)
    result = api.PostUpdate(response, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)

# Get tweet by mentions
mentions = api.GetMentions()
print(mentions[0])
createID = mentions[0].id

#for mention in mentions:
print("Mention text: ", mentions[0].text)

#play the demo, to be extended
#for tweet in mentions:
tweet = mentions[0]
food_in_tweet = detectFoodInTweet(tweet)
recipe = returnRecipe(food_in_tweet)
print(recipe)


tweetResponse(createResponse(recipe[1]), createID)
#print(createRandomResponse())
