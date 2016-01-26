from flask import Flask, jsonify, Response
from flask_restful import reqparse, abort, Api, Resource
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps, default

app = Flask("test")
api = Api(app)
mongo = PyMongo(app)

QUOTES = {
    'quote1': {'task': 'build an API'},
    'quote2': {'task': '?????'},
    'quote3': {'task': 'profit!'},
}


parser = reqparse.RequestParser()
parser.add_argument('author')
parser.add_argument('content', required=True,
help="Content cannot be blank!")


# Todo
# shows a single todo item and lets you delete a todo item
class Quote(Resource):
    def get(self, quote_id):
        quotes = mongo.db.quotes.find_one({"id": int(quote_id)})
        resp = Response(dumps({'data': quotes}, default=default),
                mimetype='application/json')
        return resp

    def delete(self, quote_id):
        print "Quote id is %s" % quote_id
        try:
            mongo.db.quotes.remove({
                'id': int(quote_id)
            })
        except Exception as ve:
            print ve
            abort(400, str(ve))
        return '', 204

    def put(self, quote_id):
        args = parser.parse_args()
        if not (args['content'] or args['author']):
            return 'Missing data', 400
        existing_quote = mongo.db.quotes.find_one({"id": int(quote_id)})
        args['content'] = args['content'] if args['content'] else existing_quote["content"]
        args['author'] = args['author'] if args['author'] else existing_quote["author"]
        try:
            mongo.db.quotes.update({
                'id': quote_id
            },{
                '$set': {
                    'content': args['content'],
                    'author': args['author']
            }
        }, upsert=False)
        except Exception as ve:
            print ve
            abort(400, str(ve))
        return 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class QuoteList(Resource):
    def get(self):
        quotes = mongo.db.quotes.find().sort("id", -1).limit(10)
        resp = Response(dumps({'data': quotes}, default=default),
                mimetype='application/json')
        return resp

    def post(self):
        args = parser.parse_args()
        quotes = mongo.db.quotes.find().sort("id", -1).limit(1)
        print quotes[0]
        args["id"] = int(quotes[0]["id"]) + 1
        print args
        try:
            mongo.db.quotes.insert(args)
        except Error as ve:
            abort(400, str(ve))

        return 201

##
## Actually setup the Api resource routing here
##
api.add_resource(QuoteList, '/api/quotes')
api.add_resource(Quote, '/api/quotes/<quote_id>')


if __name__ == '__main__':
    app.run(debug=True)