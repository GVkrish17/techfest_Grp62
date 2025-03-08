import openai

openai.api_key = "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"

models = openai.Model.list()
for model in models['data']:
    print(model['id'])