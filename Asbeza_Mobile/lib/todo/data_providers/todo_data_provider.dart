import 'dart:convert';
import 'package:asbeza_mobile_app/todo/models/models.dart';
import 'package:asbeza_mobile_app/todo/models/todo_model.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

Future<SharedPreferences> _prefs = SharedPreferences.getInstance();
Future addToSession(Map value) async {
  final SharedPreferences prefs = await _prefs;
  return prefs;
}

class TodoDataProvider {
  static final String _baseUrl = "http://10.0.2.2:5000/asbeza/api/v1";

  // method for creating item
  Future<dynamic> create(int userId, Todo todo) async {
    final int itemId = todo.item.id;

    Future<SharedPreferences> _prefs = SharedPreferences.getInstance();
    Future<String> token;
    String tokenString = "";
    token = _prefs.then((SharedPreferences prefs) {
      return (prefs.getString('token') ?? "");
    });
    tokenString = await token;

    final http.Response response = await http.post(
        Uri.parse("$_baseUrl/purchases/$itemId"),
        headers: {
          "Content-Type": "application/json",
          "X-Access-Token": await tokenString,
        },
        body: jsonEncode(
            {"is_purchased": false, "item_id": itemId, "user_id": userId}));

    if (response.statusCode == 200) {
      final res = jsonDecode(response.body);
      final item = await getItem(itemId, tokenString);

      return Todo.fromJson(res, item);
    } else {
      throw Exception("Failed to create todo");
    }
  }

  Future<List<dynamic>> fetchAll(int userId) async {
    Future<SharedPreferences> _prefs = SharedPreferences.getInstance();
    Future<String> token;
    String tokenString = "";
    token = _prefs.then((SharedPreferences prefs) {
      return (prefs.getString('token') ?? "");
    });
    tokenString = await token;

    final http.Response response = await http.get(
      Uri.parse("$_baseUrl/purchases"),
      headers: {
        "Content-Type": "application/json",
        "X-Access-Token": await tokenString,
      },
    );

    if (response.statusCode == 200) {
      final todos = jsonDecode(response.body) as List;
      print(todos);
      return todos.map((c) => TodoAll.fromJson(c)).toList();
    } else {
      throw Exception("Failed to create todo");
    }
  }

  Future<PurchaseItem> getItem(int id, String token) async {
    final response = await http.get(Uri.parse("$_baseUrl/items/$id"), headers: {
      "Content-Type": "application/json",
      'x-access-token': token,
    });

    if (response.statusCode == 200) {
      final item = jsonDecode(response.body);

      return PurchaseItem.fromJson(item);
    } else {
      throw Exception("Could not fetch the item");
    }
  }

  // // method to update item info by admin
  Future<TodoAll> update(int id, TodoAll todo) async {
    Future<SharedPreferences> _prefs = SharedPreferences.getInstance();
    Future<String> token;
    String tokenString = "";
    token = _prefs.then((SharedPreferences prefs) {
      return (prefs.getString('token') ?? "");
    });
    tokenString = await token;

    final response =
        await http.put(Uri.parse("$_baseUrl/purchases/${todo.itemId}"),
            headers: {
              "Content-Type": "application/json",
              "X-Access-Token": await tokenString,
            },
            body: jsonEncode({
              'user_id': todo.userId ?? 0,
              'item_id': todo.itemId,
              'name': todo.name,
              'max_price': todo.max_price,
              'min_price': todo.min_price,
              'is_purchased': todo.isPurchased,
            }));
    if (response.statusCode == 200) {
      return TodoAll.fromJson(jsonDecode(response.body));
    } else {
      throw Exception("Could not update the item");
    }
  }

  // // method to delete an item by admin
  Future<void> delete(int id, int item_id) async {
    Future<SharedPreferences> _prefs = SharedPreferences.getInstance();
    Future<String> token;
    String tokenString = "";
    token = _prefs.then((SharedPreferences prefs) {
      return (prefs.getString('token') ?? "");
    });
    tokenString = await token;

    final response = await http.delete(Uri.parse("$_baseUrl/purchases/$item_id"), headers: {
      "Content-Type": "application/json",
      'x-access-token': await tokenString,
    });
    if (response.statusCode != 200) {
      throw Exception("Failed to delete the item");
    }
  }
}
