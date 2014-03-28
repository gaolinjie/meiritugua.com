#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 meiritugua.com

from wtforms import TextField, HiddenField, validators
from lib.forms import Form

class ReplyForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写回复内容"),
    ])

    tid = TextField('Tid', [
        validators.Required(message = "要回复的帖子不明确"),
    ])

class PostForm(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写视频介绍"),
        validators.Length(min = 6, message = "介绍长度过短（3-140个字符）"),
        validators.Length(max = 280, message = "介绍长度过长（3-140个字符）"),
    ])

    link = TextField('Link', [
        validators.Required(message = "请填写视频链接"),
    ])

    channel = TextField('Channel', [
        validators.Required(message = "请选择视频频道"),
    ])

class PostForm2(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写视频介绍"),
        validators.Length(min = 3, message = "介绍长度过短（3-56个字符）"),
        validators.Length(max = 156, message = "介绍长度过长（3-56个字符）"),
    ])

    link = TextField('Link', [
        validators.Required(message = "请填写视频链接"),
    ])

class ChannelForm(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写频道介绍"),
        validators.Length(min = 3, message = "介绍长度过短（3-56个字符）"),
        validators.Length(max = 156, message = "介绍长度过长（3-56个字符）"),
    ])

    name = TextField('Name', [
        validators.Required(message = "请填写频道名称"),
    ])

    subnav = TextField('Subnav', [
        validators.Required(message = "请选择频道类别"),
    ])

class ChannelForm2(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写频道介绍"),
        validators.Length(min = 3, message = "介绍长度过短（3-56个字符）"),
        validators.Length(max = 156, message = "介绍长度过长（3-56个字符）"),
    ])

    name = TextField('Name', [
        validators.Required(message = "请填写频道名称"),
    ])

    nav = TextField('Nav', [
        validators.Required(message = "请选择频道类别"),
    ])


class ReplyEditForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写回复内容"),
    ])

class CreateMessageForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写帖子内容"),
    ])






class CreateForm(Form):
     title = TextField('Title', [
         validators.Required(message = "请填写帖子标题"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-100个字符）"),
         validators.Length(max = 100, message = "帖子标题长度过长（3-100个字符）"),
     ])

     intro = TextField('Intro', [
         validators.Required(message = "请填写帖子简介"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-400个字符）"),
         validators.Length(max = 400, message = "帖子标题长度过长（3-400个字符）"),
     ])
 
     content = TextField('Content', [
         validators.Required(message = "请填写帖子内容"),
     ])

     thumb = TextField('Thumb', [
         validators.Length(min = 0, message = "thumb"),
     ])

     channel = TextField('Channel', [
         validators.Required(message = "请选择帖子频道"),
     ])

     visible = TextField('Visible', [
         validators.Required(message = "请选择帖子是否公开"),
     ])


     x1 = TextField('X1', [
         validators.Required(message = "x1"),
     ])

     y1 = TextField('Y1', [
         validators.Required(message = "y1"),
     ])

     x2 = TextField('X2', [
         validators.Required(message = "x2"),
     ])

     y2 = TextField('Y2', [
         validators.Required(message = "y2"),
     ])

     tag = TextField('Tag', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     via = TextField('Via', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

class EditForm(Form):
     title = TextField('Title', [
         validators.Required(message = "请填写帖子标题"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-100个字符）"),
         validators.Length(max = 100, message = "帖子标题长度过长（3-100个字符）"),
     ])

     intro = TextField('Intro', [
         validators.Required(message = "请填写帖子简介"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-400个字符）"),
         validators.Length(max = 400, message = "帖子标题长度过长（3-400个字符）"),
     ])
 
     content = TextField('Content', [
         validators.Required(message = "请填写帖子内容"),
     ])

     channel = TextField('Channel', [
         validators.Required(message = "请选择帖子频道"),
     ])

     visible = TextField('Visible', [
         validators.Required(message = "请选择帖子是否公开"),
     ])

     thumb = TextField('Thumb', [
         validators.Length(min = 0, message = "thumb"),
     ])


     x1 = TextField('X1', [
         validators.Length(min = 0, message = "x1"),
     ])

     y1 = TextField('Y1', [
         validators.Length(min = 0, message = "y1"),
     ])

     x2 = TextField('X2', [
         validators.Length(min = 0, message = "x2"),
     ])

     y2 = TextField('Y2', [
         validators.Length(min = 0, message = "y2"),
     ])

     tag = TextField('Tag', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     via = TextField('Via', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])


class AddForm(Form):
     title = TextField('Title', [
         validators.Required(message = "请填写帖子标题"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-100个字符）"),
         validators.Length(max = 100, message = "帖子标题长度过长（3-100个字符）"),
     ])

     intro = TextField('Intro', [
         validators.Required(message = "请填写帖子简介"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-400个字符）"),
         validators.Length(max = 400, message = "帖子标题长度过长（3-400个字符）"),
     ])
 
     content = TextField('Content', [
         validators.Required(message = "请填写帖子内容"),
     ])

     thumb = TextField('Thumb', [
         validators.Length(min = 0, message = "thumb"),
     ])

     channel = TextField('Channel', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     visible = TextField('Visible', [
         validators.Required(message = "请选择帖子是否公开"),
     ])


     x1 = TextField('X1', [
         validators.Required(message = "x1"),
     ])

     y1 = TextField('Y1', [
         validators.Required(message = "y1"),
     ])

     x2 = TextField('X2', [
         validators.Required(message = "x2"),
     ])

     y2 = TextField('Y2', [
         validators.Required(message = "y2"),
     ])

     tag = TextField('Tag', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     price = TextField('Price', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     link = TextField('Link', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     label = TextField('Label', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])


class EditItemForm(Form):
     title = TextField('Title', [
         validators.Required(message = "请填写帖子标题"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-100个字符）"),
         validators.Length(max = 100, message = "帖子标题长度过长（3-100个字符）"),
     ])

     intro = TextField('Intro', [
         validators.Required(message = "请填写帖子简介"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-400个字符）"),
         validators.Length(max = 400, message = "帖子标题长度过长（3-400个字符）"),
     ])
 
     content = TextField('Content', [
         validators.Required(message = "请填写帖子内容"),
     ])

     channel = TextField('Channel', [
         validators.Required(message = "请选择帖子频道"),
     ])

     visible = TextField('Visible', [
         validators.Required(message = "请选择帖子是否公开"),
     ])

     thumb = TextField('Thumb', [
         validators.Length(min = 0, message = "thumb"),
     ])

     x1 = TextField('X1', [
         validators.Length(min = 0, message = "x1"),
     ])

     y1 = TextField('Y1', [
         validators.Length(min = 0, message = "y1"),
     ])

     x2 = TextField('X2', [
         validators.Length(min = 0, message = "x2"),
     ])

     y2 = TextField('Y2', [
         validators.Length(min = 0, message = "y2"),
     ])

     tag = TextField('Tag', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     price = TextField('Price', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     link = TextField('Link', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])

     label = TextField('Label', [
         validators.Length(min = 0, message = "帖子标题长度过短（3-100个字符）"),
     ])
