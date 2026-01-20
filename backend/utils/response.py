from flask import jsonify

def success_response(data=None, msg="成功"):
    return jsonify({
        "code": 200,
        "msg": msg,
        "data": data
    })

def error_response(msg="失败", code=400):
    return jsonify({
        "code": code,
        "msg": msg,
        "data": None
    })
