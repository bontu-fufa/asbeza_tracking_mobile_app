from flask import Blueprint, request, jsonify
from flask_restplus import Api, Resource
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from marshmallow import fields, Schema


from asbeza.ma import *
from asbeza.models.models import *

#BLUEPRINT
bp = Blueprint('application', __name__, url_prefix='/asbeza/api/v1')
api=Api(bp, version='1.0', title = 'Asbeza API', description = 'Asbeza Tracker API' )

#SCHEMA

user_schema = ma.UserSchema()
users_schema = ma.UserSchema(many=True)

item_schema = ma.ItemSchema()
items_schema = ma.ItemSchema(many=True)

report_schema = ma.ReportSchema()
reports_schema = ma.ReportSchema(many=True)

user = api.model("User",{
    'user_name' : fields.String,
    'email': fields.String,
    'password': fields.String,
})

item = api.model("Item",{
    'name' : fields.String,
    'min_price': fields.String,
    'max_price': fields.String,
})

report = api.model("Report",{
    'location' : fields.String,
    'description': fields.String,
    'status': fields.String,
    'like_counts': fields.Integer,
    'reporter_id': fields.Integer,
    'item_id': fields.Integer,
})


#NAMESPACE
userNamespace = api.namespace("Asbeza", path="/users")
itemNamespace = api.namespace("Asbeza", path="/items")
reportNamespace = api.namespace("Asbeza", path="/users/<int:id>/reports")
purchaseNamespace = api.namespace("Asbeza", path="/users/<int:id>/purchases")

@userNamespace.route("")
class userResource(Resource):

    def get(self):
        """
        Get all the Users
        """
      
        return users_schema.dump(User.get_all_users())
        

        # return {"a" : "aaa", "b" : "bbb"}
    @api.expect(user)
    def post(self):
        """
        Create a new User
        """
        new_user = User()
        new_user.name = request.json['user_name']
        new_user.email = request.json['email']
        new_user.password = request.json['password']
        new_user.user_type = request.json['user_type']

        new_user.save()

        return user_schema.dump(new_user)
        
@userNamespace.route('/<int:id>')
class userResourceWithID(Resource):

    def get(self, id):
        """
        Get a User
        """
        user = User.get_one_user(id)

        if not user:
            return "User Not Found", 404
        return user_schema.dump(user)

@userNamespace.route('/login')
class userResourceLogin(Resource):

    @api.expect(user)
    def post(self):
        """
        Search for user
        """
        name = request.json['user_name']
        password = request.json['password'] 
        result = User.query.filter_by(name=name).first()
        if result:
            if result.password == password:
                return {"message":"logged in", "currentUserId": result.id, "currentUserName": result.name, "currentUserEmail": result.email, "currentUserType": result.user_type}
        return {"message":"not logged in"} 



@itemNamespace.route("")
class itemResource(Resource):

    def get(self):
        """
        Get all the Items
        """
      
        return items_schema.dump(Item.get_all_items())
        
    @api.expect(item)
    def post(self):
        """
        Create a new Item
        """
        new_item = Item()
        new_item.name = request.json['name']
        new_item.min_price = request.json['min_price']
        new_item.max_price = request.json['max_price']

        new_item.save()

        return item_schema.dump(new_item)

@itemNamespace.route('/<int:id>')
class itemResourceWithID(Resource):

    def get(self, id):
        """
        Get an Item
        """
        item =Item.get_one_item(id)

        if not item:
            return "Item Not Found", 404
        return item_schema.dump(item)

    def put(self, id):
        """
        Updates an item
        """
        item = Item.query.filter_by(id=id).first()

        if not item:
            return "Item Not Found", 404

        json = request.get_json(force=True)
        item.name = json["name"]
        item.min_price = json["min_price"]
        item.max_price= json["max_price"]

        item.save()

        return item_schema.dump(item)

    def delete(self,id):

        item = Item.query.filter_by(id=id).first()

        params = {"id": id}
        statement = """DELETE  from items WHERE id =:id"""
                
                
        db.session.execute(statement, params)
        db.session.commit()

        return {"message" : "Item successfully deleted"},

 
@reportNamespace.route("")
class reportResource(Resource):

    def get(self, id):
        """
        Get all the reports
        """
      
        return reports_schema.dump(Report.get_all_reports())
        

    @api.expect(report)
    def post(self, id):
        """
        Create a new report
        """
        new_report = Report()
        new_report.location = request.json['location']
        new_report.description = request.json['description']
        new_report.status = "pending"
        new_report.like_counts = 0
        new_report.reporter_id = id
        new_report.item_id=request.json['item_id']

        new_report.save()

        return report_schema.dump(new_report)


@reportNamespace.route("/<int:report_id>")
class reportResourceWithID(Resource):

    def get(self, id, report_id):
        """
        Get report with id of report_id
        """
        report = Report.get_one_report(report_id)
        if not report:
            return "Report not found", 404
        
        return report_schema.dump(report)

    def delete(self, id, report_id):
        """
        Delete a report with id of report_id
        """

        report = Report.get_one_report(report_id)
        report.delete()
        db.session.commit()
      
        return report_schema.dump(report)


    @api.expect(report)
    def put(self, id, report_id):
        """
        Update a report with id of report_id
        """
        print(request.json)
        report = Report.get_one_report(report_id)
        if request.json.get('location'):
            report.location = request.json['location']
        if request.json.get('description'):
            report.description = request.json['description']
        if request.json.get('status'):
            report.status = request.json['status']
        
        if str(request.json.get('like_counts')):
            likeCount = report.like_counts
            newLikeCount = request.json['like_counts']
            if newLikeCount == likeCount + 1:
                print(type(newLikeCount))
                params = {"user_id": id, "report_id": report_id}
                statement = """insert into likedReports(user_id, report_id) values(:user_id, :report_id)"""
                db.session.execute(statement, params)
                db.session.commit()

            if newLikeCount == likeCount - 1:
                print(type(newLikeCount))
                params = {"user_id": id, "report_id": report_id}
                statement = """delete from likedReports where user_id=:user_id AND report_id=:report_id"""
                db.session.execute(statement, params)
                db.session.commit()
            report.like_counts = request.json['like_counts']

        report.reporter_id = id

        report.save()

        return report_schema.dump(report)
        
@purchaseNamespace.route("")
class purchaseResource(Resource):

    def get(self, id):
        params = {"user_id": id}
        statement = """select * from purchasedGoods where user_id=:user_id"""
        purchases = db.session.execute(statement, params).all()

        purchases_list = []
        for purchase in purchases:
            purchase_json = {
                "user_id": purchase.user_id,
                "item_id": purchase.item_id,
                "is_purchased": purchase.is_purchased
            }
            purchases_list.append(purchase_json)
        
        return jsonify(purchases_list)

@purchaseNamespace.route("/<int:item_id>")
class purchaseResourceWithID(Resource):

    def get(self, id, item_id):
        params = {"user_id": id, "item_id": item_id}
        statement = """select * from purchasedGoods where user_id=:user_id AND item_id:item_id"""
        purchase = db.session.execute(statement, params).one()

        return purchase
        
    def post(self, id, item_id):
        params = {"user_id": id, "item_id": item_id}
        statement = """insert into purchasedGoods(user_id, item_id, is_purchased) values(:user_id, :item_id, false)"""
        db.session.execute(statement, params)
        db.session.commit()

        statement = """select * from purchasedGoods where user_id=:user_id AND item_id=:item_id"""
        purchase = db.session.execute(statement, params).one()

        purchase_json = {
            "user_id": purchase.user_id,
            "item_id": purchase.item_id,
            "is_purchased": purchase.is_purchased
        }

        return jsonify(purchase_json)

    def put(self, id, item_id):
        is_purchased = request.json["is_purchased"]
        params = {"user_id": id, "item_id": item_id}

        if is_purchased == True:
            statement = """update purchasedGoods set is_purchased=true where user_id=:user_id and item_id=:item_id"""
        else:
            statement = """update purchasedGoods set is_purchased=false where user_id=:user_id and item_id=:item_id"""

        db.session.execute(statement, params)
        db.session.commit()

        statement = """select * from purchasedGoods where user_id=:user_id AND item_id=:item_id"""
        purchase = db.session.execute(statement, params).one()

        purchase_json = {
            "user_id": purchase.user_id,
            "item_id": purchase.item_id,
            "is_purchased": purchase.is_purchased
        }

        return jsonify(purchase_json)

    def delete(self, id, item_id):
        params = {"user_id": id, "item_id": item_id}
        statement = """select * from purchasedGoods where user_id=:user_id AND item_id=:item_id"""
        purchase = db.session.execute(statement, params).one()
        
        statement = """delete from purchasedGoods where user_id=:user_id AND item_id=:item_id"""
        db.session.execute(statement, params)
        db.session.commit()

        purchase_json = {
            "user_id": purchase.user_id,
            "item_id": purchase.item_id,
            "is_purchased": purchase.is_purchased
        }

        return jsonify(purchase_json)
