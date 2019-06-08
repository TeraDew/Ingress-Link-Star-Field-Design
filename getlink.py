# -*- coding: utf-8 -*-
import json
import logging
import os
import math
from Vector import *
#import numpy as np


class Portal(object):
    def __init__(self, name, lat, lng):
        self.name = name
        self.lat = lat
        self.lng = lng

        self.x = math.cos(self.lat/180.0*math.pi)
        math.cos((self.lng/180.0*math.pi))
        self.y = math.sin(self.lat/180.0*math.pi)
        math.cos((self.lng/180.0*math.pi))
        self.z = math.sin(self.lng/180.0*math.pi)

        self.array = Vector([self.x, self.y, self.z])

    def portal2dict(self):
        return {
            'lat': self.lat,
            'lng': self.lng
        }

    def __str__(self):
        return self.name


def is_left(a, b, c):
    normal_vector = a.array @ b.array
    return c.array * normal_vector > 0


def is_inner(triangle, d):
    a, b, c = triangle.a, triangle.b, triangle.c
    if a.array == d.array or b.array == d.array or c.array == d.array:
        return False
    if not is_left(a, b, c):
        b, c = c, b
    return is_left(a, b, d) and is_left(b, c, d) and is_left(c, a, d)


class Triangle(object):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def inner_portal_count(self, portal_list):
        n = 0
        inner_list = []
        for portal in portal_list:
            if is_inner(self, portal):
                n = n+1
                inner_list.append(portal)
        return n, inner_list

    def __str__(self):
        return "-".join((self.a.name, self.b.name, self.c.name))


def get_convex_hull(portal_list):
    apex = portal_list[0]
    inner_list = list(portal_list)

    distance_list = []
    for portal in inner_list:
        distance_list.append(abs(apex.array-portal.array))

    seed_index = distance_list.index(max(distance_list))
    convex_list = []
    # print(inner_list[seed_index].name)
    convex_list.append(inner_list[seed_index])
    # inner_list.pop(seed_index)
    while(True):
        for a in inner_list:
            break_flag = 0
            inner_flag = False
            for b in inner_list:
                if(a.array == b.array or (convex_list[-1].array == b.array)):
                    continue
                if is_left(convex_list[-1], a, b):
                    continue
                else:
                    inner_flag = True
                    break
            if inner_flag:
                continue

            else:
                convex_list.append(a)
                inner_list.remove(a)

                if (convex_list[0].array == convex_list[-1].array):
                    convex_list.pop()
                    return convex_list, inner_list
                break_flag = 1
                break
            if break_flag:
                break


def divide_convex_hull(convex_list, i):
    try:
        triangle_list = []
        n = len(convex_list)
        for j in range(n-2):
            triangle_list.append(
                Triangle(convex_list[i-2-j], convex_list[i-1-j], convex_list[i]))
        return triangle_list
    except IndexError as e:
        print("IndexError:", e)


def get_initial_line():
    pass


def draw_line(point_a, point_b):
    pass
    line = {'type': 'polyline', 'latLngs': [
        point_a.portal2dict(), point_b.portal2dict()], 'color': '#0099FF'}
    return line


def draw_triangle(triangle):
    polyline = []

    polyline.append(draw_line(triangle.a, triangle.b))
    polyline.append(draw_line(triangle.b, triangle.c))
    polyline.append(draw_line(triangle.c, triangle.a))
    return polyline


def draw_tri_link(triangle, p):
    polyline = []
    polyline.append(draw_line(triangle.a, p))
    polyline.append(draw_line(triangle.b, p))
    polyline.append(draw_line(triangle.c, p))
    return polyline


def get_triangles(triangle, inner_list, polyline):
    if len(inner_list) == 0:
        return polyline
    if len(inner_list) == 1:
        polyline += draw_tri_link(triangle, inner_list[0])
        return polyline

    for p in inner_list:
        left_list = []
        right_list = []
        t = Triangle(triangle.b, triangle.c, p)
        bottom_flag = True
        for inner_p in inner_list:
            if p == inner_p:
                continue
            if is_inner(t, inner_p):
                bottom_flag = False
                break
        if bottom_flag:
            polyline += draw_tri_link(triangle, p)

            for tem_point in inner_list:
                if p == tem_point:
                    continue
                if is_left(p, triangle.a, tem_point):
                    left_list.append(tem_point)
                else:
                    right_list.append(tem_point)
            if is_left(p, triangle.a, triangle.b):
                triangle_left = Triangle(triangle.a, triangle.b, p)
                triangle_right = Triangle(triangle.a, triangle.c, p)
            else:
                triangle_left = Triangle(triangle.a, triangle.c, p)
                triangle_right = Triangle(triangle.a, triangle.b, p)
            get_triangles(triangle_left, left_list, polyline)
            get_triangles(triangle_right, right_list, polyline)
            break


def get_divided(portal_list, convex_list):
    if portal_list[0] in convex_list:
        inner_list = []
        triangle_list = divide_convex_hull(
            convex_list, convex_list.index(portal_list[0]))
        for triangle in triangle_list:
            if (triangle.a != portal_list[0]):
                triangle.a, triangle.b = triangle.b, triangle.a
            if(triangle.a != portal_list[0]):
                triangle.a, triangle.c = triangle.c, triangle.a
            temp, temp_inner_list = triangle.inner_portal_count(
                portal_list)
            inner_list.append(temp_inner_list)
        return triangle_list, inner_list
    else:
        apex = portal_list[0]
        n = len(convex_list)
        inner_count_list = [0]*n
        divide_list = []
        inner_group = []

        for i in range(n):
            inner_list = []
            triangle_list = divide_convex_hull(convex_list, i)
            divide_list.append(triangle_list)
            for triangle in triangle_list:
                if is_inner(triangle, apex):
                    inner_count_list[i], temp_inner_list = triangle.inner_portal_count(
                        portal_list)
                    inner_list.append(temp_inner_list)
                else:
                    temp, temp_inner_list = triangle.inner_portal_count(
                        portal_list)
                    inner_list.append(temp_inner_list)
            inner_group.append(inner_list)

        best_divide_list = divide_list[inner_count_list.index(
            max(inner_count_list))]
        best_inner_list = inner_group[inner_count_list.index(
            max(inner_count_list))]

        for tri, inner in zip(best_divide_list, best_inner_list):
            if is_inner(tri, apex):
                tri1 = Triangle(apex, tri.a, tri.b)
                tri2 = Triangle(apex, tri.b, tri.c)
                tri3 = Triangle(apex, tri.c, tri.a)
                temp, tri1_inner = tri1.inner_portal_count(inner)
                temp, tri2_inner = tri2.inner_portal_count(inner)
                temp, tri3_inner = tri3.inner_portal_count(inner)
                best_divide_list.remove(tri)
                best_inner_list.remove(inner)
                best_divide_list += [tri1, tri2, tri3]
                best_inner_list += [tri1_inner, tri2_inner, tri3_inner]

        return best_divide_list, best_inner_list

        # polyline = []

        # for i in range(len(best_divide_list)):
        #     if is_inner(best_divide_list[i], apex):
        #         pass
        #     else:
        #         polyline += get_triangles(best_divide_list[i],
        #                                   best_inner_list[i], polyline)

        # for t in best_divide_list:
        #     polyline += draw_triangle(t)
        # return polyline

        # json_str = json.dumps(polyline)
        # with open('result.txt', 'w') as f:
        #    f.write(json_str)
        # return polyline, best_divide_list


def get_portals(filename):
    '''

    '''
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        p_dict = json.loads(f.read())

        portal_list = []
        for group in p_dict["portals"]:  # 输出带序号的portal名，选择顶点
            for portal in p_dict["portals"][group]["bkmrk"]:
                latlng = p_dict["portals"][group]["bkmrk"][portal]["latlng"]
                temp_portal = Portal(p_dict["portals"][group]["bkmrk"][portal]["label"], float(
                    latlng.split(",")[0]), float(latlng.split(",")[1]))
                portal_list.append(temp_portal)

    print('apex name: ' + portal_list[0].name)

    return portal_list


def test_get_triangles():

    portal_list = get_portals('single_triangel.txt')
    convex, inner = get_convex_hull(portal_list)
    polyline = []
    triangle_list = divide_convex_hull(convex, 0)
    test = triangle_list[0]
    polyline += draw_triangle(test)

    get_triangles(test, inner, polyline)

    json_str = json.dumps(polyline)
    with open('test_get_triangle_result.txt', 'w') as f:
        f.write(json_str)


def test_get_divided():

    temp_no = 1
    for filename in os.listdir('.'):
        print(temp_no, filename)
        temp_no += 1

    print("选择portal列表文件序号")

    file_no = int(input())
    filename = os.listdir('.')[file_no - 1]
    print(filename)

    portal_list = get_portals(filename)
    convex, inner = get_convex_hull(portal_list)

    portal_n = len(portal_list)
    convex_n = len(convex)
    inner_n = portal_n-convex_n
    link_n = 2*convex_n-3+3*inner_n
    field_n = 3*inner_n+convex_n-2

    print('portal\t内点\t外点\tlink\tfield\tap\n%d\t%d\t%d\t%d\t%d\t%d' % (
        portal_n, inner_n, convex_n, link_n, field_n, link_n*313+field_n*1250))

    triangle_list, inner_portal_list = get_divided(portal_list, convex)

    polyline = []

    for triangle, inner_list in zip(triangle_list, inner_portal_list):
        polyline += draw_triangle(triangle)
        #print("%s 的内点个数：%d" % (triangle, len(inner_list)))
        get_triangles(triangle, inner_list, polyline)

    json_str = json.dumps(polyline)
    (result_filename, temp) = os.path.splitext(filename)
    result_filename += '_result.txt'
    with open(result_filename, 'w') as f:
        f.write(json_str)


if __name__ == "__main__":

    test_get_divided()
