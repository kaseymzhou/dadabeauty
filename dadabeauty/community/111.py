@logging_check
def comment(request):
    if request.method == 'POST':
        data = request.body
        if not data:
            result = {'code': '30111', 'error': '请填写评论'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        blog_id = json_obj.get('blog_id')
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        Comment.objects.create(content=content,uid=uid,b_id = blog_id)

        # 判断是否在redis中曾经有设立过计数key
        blog_comment_count = r.hexists('comment:count',blog_id)
        if blog_comment_count is False:
            r.hset('comment:count',blog_id,0)
        # redis做评论计数
        r.hincrby('comment:count',blog_id,1)
        result = {'code':200,'data':'评论成功'}
        return JsonResponse(result)

    if request.method == 'DELETE':
        data = request.body
        if not data:
            result = {'code': '30112', 'error': '删除失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        comment_id = json_obj.get('comment_id')
        comments = Comment.objects.filter(id=comment_id)
        if not comments:
            return JsonResponse({'code': '30113', 'error': '无法删除该评论'})
        comment = comments[0]
        # 修改评论isActive属性为False
        comment.isActive=False
        comment.save()
        # redis做评论计数
        sku_id = comment.sku_id
        r.hincrby('comment:count', sku_id, -1)
        result = {'code': 200, 'data': '删除评论成功'}
        return JsonResponse(result)

# 评论的回复
class Reply(View):
    @logging_check
    def post(self,request):
        data = request.body
        if not data:
            result = {'code': '30104', 'error': '请填写回复信息'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        content = json_obj.get('content')
        uid = json_obj.get('uid')
        c_id = json_obj.get('c_id')
        Reply.objects.create(content=content, uid=uid,c_id=c_id)
        # redis做评论计数
        comments = Comment.objects.filter(id=c_id)
        comment = comments[0]
        sku_id = comment.sku_id
        r.hincrby('peoducts:comment', sku_id, 1)
        # mysql数据库录入
        result = {'code':200,'data':'回复成功'}
        return JsonResponse(result)
    @logging_check
    def delete(self, request):
        data = request.body
        if not data:
            result = {'code': '30105', 'error': '删除失败'}
            return JsonResponse(result)
        json_obj = json.loads(data)
        reply_id = json_obj.get('reply_id')
        replies = Reply.objects.filter(id=reply_id)
        if not replies:
            return JsonResponse({'code': 30106, 'error': '无法删除该回复'})
        reply = replies[0]
        reply.isActive = False
        reply.save()
        # redis做评论计数
        c_id = reply.c_id
        comments = Comment.objects.filter(id=c_id)
        comment = comments[0]
        sku_id = comment.sku_id
        r.hincrby('peoducts:comment', sku_id, -1)
        result = {'code': 200, 'data': '删除回复成功'}
        return JsonResponse(result)