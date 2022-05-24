from flask import jsonify


class Result:
    @classmethod
    def succ(cls, data):
        return jsonify({
            'code': 200,
            'msg': '操作成功',
            'data': data
        })

    @classmethod
    def fail(cls, msg):
        return jsonify({
            'code': 400,
            'msg': msg,
            'data': None
        })

    @classmethod
    def fail(cls, msg, data):
        return jsonify({
            'code': 400,
            'msg': msg,
            'data': data
        })
