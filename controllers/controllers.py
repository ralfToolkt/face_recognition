# -*- coding: utf-8 -*-
from odoo import http

from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception

import json
import string
import random

import face_recognition as fr
import io
import base64
from PIL import Image
import cv2
import numpy as np


# Take in base64 string and return cv image
def stringToRGB(base64_string):
    imgdata = base64.b64decode(str(base64_string))
    image = Image.open(io.BytesIO(imgdata))
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

def get_face_encoding_from_base64(base64String):
    image = fr.load_image_file(stringToRGB(base64_string))
    image_encoding = fr.face_encodings(image)
    return image_encoding


class BaseRest(http.Controller):
    @http.route('/api/auth', auth='none', type='http', methods=['POST'], csrf=False)
    @serialize_exception
    def index(self, **kw):
        """ user, password """
        print(serialize_exception)
        response = {}
        if 'user' in kw and 'password' in kw:
            session = request.session
            login = request.session.authenticate(
                session['db'], kw['user'], kw['password']
            )
            print(login)
            if not login:
                response['status'] = 'denied'
                return request.make_response(json.dumps(response),[('Access-Control-Allow-Origin', '*')])
            
            users = request.env['res.users'].sudo().search([('login', '=', kw['user'])])
            if users:
                for user in users:
                    if not user['token']:
                        token = self.get_token(user)                    
                    response = {
                        "name" : user['name'] or "",
                        "user" : user['login'] or "",
                        "token": user['token'] or token,
                        "email" : user['email'],
                        "profile": True if user['profile'] else False
                    }
            if not response:
                response['status'] = 'error'
            return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])
        else:
            response['status'] = 'error'
            return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])

    def get_token(self, user):
        length = 25
        letters = string.ascii_letters + '1234567890'
        token = ''.join(random.choice(letters) for i in range(length))
        print("Random string is:", token)
        user.sudo().write({"token": token})
        return token


    @http.route('/api/attendance', auth='none', type='http', methods=['POST'], csrf=False)
    def attendance(self, **kw):
        response = {}
        user = request.env['res.users'].sudo().search([('token', '=', kw['token'])])
        if user:
            image_receive = get_face_encoding_from_base64(kw['image'])
            users = request.env['res.users'].sudo().search([('active', '=', True), ('profile', '!=', False)])
            print(users)
            known_faces = []
            known_face_names = []
            for user_w_profile in users:
                known_faces.append(get_face_encoding_from_base64(user_w_profile.profile)
                known_face_names.append(user_w_profile.name)
            if len(image_receive) > 0:
                print(known_face_names)
                for encoding in image_receive:                    
                    # image_user = get_face_encoding_from_base64(user.profile)                
                    result = fr.compare_faces(known_faces, encoding)
                    name = 'unknown'

                    # face_distances = fr.face_distance(known_faces, encoding)
                    # best_match_index = np.argmin(face_distances)
                    # if result[best_match_index]:
                    #     name = known_face_names[best_match_index]
                    
                    print(result)
                    if True in result:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]
                    print(name)
                    response['name'] = name
                    # if result[0]:
                    #     if user.check_attendance(kw['longitude'], kw['latitude'], kw['address']):
                    #         response['result'] = 'Attendace Success'
                    #     else:
                    #         response['result'] = 'Attendace Today Already recorded'
                    # else:
                    #     response['result'] = 'Cant Recognize you, Please try again'
                    # response['result'] = '%s'%result[0]
            else:
                response['result'] = 'Cant Recognize, Please try again'
        else:
            response['result'] = 'error'
        return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])

    @http.route('/api/attendance-logs', auth='none', type='http', methods=['GET'], csrf=False)
    def get_attendance_logs(self, **kw):
        response = {'logs': []}
        user = request.env['res.users'].sudo().search([('token', '=', kw['token'])])
        print(user)
        if user:
            results = request.env['attendances'].sudo().search([('user_id', '=', user.id)])
            print(results)
            for res in results:
                response['logs'].append({
                    'id': res.id,
                    'date_time': '%s'%res.date_time,
                    'latitude': res.latitude,
                    'longitude': res.longitude,
                    'address': res.address,
                })
        return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])

    @http.route('/api/register-face', auth='none', type='http', methods=['POST'], csrf=False)
    def registerface(self, **kw):
        response = {}
        user = request.env['res.users'].sudo().search([('token', '=', kw['token'])])
        if user:
            user.write({
                "profile": kw['image']
            }) 
            response = {'result': 'success'}
        return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])

    @http.route('/hello', auth='none', type='http', methods=['GET'], csrf=False)
    def hello(self):
        return 'Hello, World'
