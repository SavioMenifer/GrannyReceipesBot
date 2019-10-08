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
def detectFoodInTweet(tweet_text):
    response = sp_api.detect_food_in_text(tweet_text)
    data = response.json()
    return data["annotations"]

def getRecipeDetails(json_recipe):
    if len(json_recipe) > 0:
        response = sp_api.get_recipe_information(json_recipe[0]['id'])
        print(response.headers['X-API-Quota-Used'], "points used today.") #print spoonacular quota used.
        data = response.json()
        return [json_recipe[0]['id'], json_recipe[0]['title'], json_recipe[0]['image'], data['sourceUrl']]
    else:
        return None

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
        print("Found a dish!", dishes[0]['annotation'])
        response = sp_api.search_recipes_complex(query = dishes[0]['annotation'], number = 1, includeIngredients = ingredients_string)
        search_result = response.json()
        recipes = getRecipeDetails(search_result['results'])
        if recipes:
            return recipes
    if len(ingredients) > 0:
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
    ['header', 'Hello dear', 'Hello lovely' , 'Hello my dear', 'Thanks for your message'],
    ['randomReason',
         'Hello?... My hearing aid is not working properly.', 'Oops... deary me! I forgot my reading glasses.', 
         'Yeah sorry... Didn\'t know you were talking to me.', 'Back in my day, we did not use those ingredients.'],
    ['randomIngredients', 'Could you repeat those ingredients for me darling?', 'What ingredients did you mention dear?',
    'It would be marvellous if you can tell me those ingredients again, darling. Just one more time.'],    
    ['closure', 'Tell me if you liked it!', 'Enjoy cooking!', 'Granny out.', 'Have a nice meal!', 'Bon Appetite!',
     'Make haste and start now, so you can enjoy your marvellous meal sweetheart.'], 
    ['foundrecipe', 'Granny recommends ', 'I would make ', 'you should try the ', 'you should definitely cook ', 'I wrote this one on paper, let me see. Ah! '],
    ]
    return sentences[number][randrange(1, len(sentences[number]))]

def createResponse(title, sourceUrl):
    response = ""
    header = grandmaSentences(0)
    foundRecipe = grandmaSentences(4)
    closure = grandmaSentences(3)
    response = header + ", " + foundRecipe + title + ". " + closure + "\n" + sourceUrl
    return response

def createRandomResponse():
    response = ""
    randomIngredients = grandmaSentences(2)
    randomReason = grandmaSentences(1)
    response = randomReason + " " + randomIngredients
    return response

def tweetResponse(response, tweet_id):
    print("Posting reply...")
    print("tweet id", tweet_id)
    print(response)
    result = api.PostUpdate(response, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)


print("Script started.")

mention_stream = api.GetStreamFilter(None, ['@BotGranny'])

while True:
    for tweet in mention_stream:
        print("Received mention:", tweet['text'])
        createID = tweet['id']

        food_in_tweet = detectFoodInTweet(tweet['text'])
        recipe = returnRecipe(food_in_tweet)
        if recipe:
            print("Recipe found:", recipe)
            response = createResponse(recipe[1], recipe[3])
        else:
            print("Recipe not found!")
            response = createRandomResponse()

        tweetResponse(response, createID)
        print("Reply posted.")
