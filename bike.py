import argparse
import collections
import csv
import json
import glob
import math
import os
import pandas
import re
import requests
import string
import sys
import time
import xml
import urllib

class Bike():
    def __init__(self, baseURL, station_info, station_status):
        self.response = requests.get(baseURL + station_status)
        self.status = requests.get(baseURL + station_info)
        self.baseUr = baseURL
        self.station_info = station_info
        self.station_status = station_status
        # initialize the instance
        pass

    def total_bikes(self):
        loaded_json = self.response.json()
        sum_total=0
        for row in loaded_json['data']['stations']:
            if row and "num_bikes_available" in row.keys():
                sum_total += row["num_bikes_available"]
        return sum_total

    def total_docks(self):
        loaded_json = self.response.json()
        sum_total = 0
        for row in loaded_json['data']['stations']:
            if row and "num_docks_available" in row.keys():
                sum_total += row["num_docks_available"]
        return sum_total # return the total number of docks available

    def percent_avail(self, station_id):
        # return the percentage of available docks
        loaded_json = self.response.json()
        string_return = ""
        isaninteger = isinstance(station_id, int)
        if isaninteger:
            num_bikes_available = 0
            num_docks_available = 0
            percentage = 0
            string_percentage = '%'
            for row in loaded_json['data']['stations']:
                if row and "num_docks_available" and "num_bikes_available" in row.keys():
                    row_num = int(row["station_id"])
                    if row_num == station_id:
                        num_bikes_available = row["num_bikes_available"]
                        num_docks_available = row["num_docks_available"]
                        percentage = math.floor((num_docks_available / (num_bikes_available + num_docks_available))*100)
                        string_return = (str(percentage)+string_percentage)
        else:
            string_return = ""
        return string_return

    def closest_stations(self, latitude, longitude):
        loaded_json = self.status.json()
        first_closest = 0.00
        second_closest = 0.00
        third_closest = 0.00
        temp = 0.00
        temp2 = 0.00
        new_dict = {}
        for row in loaded_json['data']['stations']:
            row_lat = float(row["lat"])
            row_lon = float(row["lon"])
            distance = self.distance(latitude, longitude, row_lat, row_lon)
            temp_name = row["station_id"]
            temp_num = row['name']
            #print(distance)
            if distance < first_closest or first_closest == 0.00: #first closest
                temp = first_closest
                temp2 = second_closest
                first_closest = distance
                second_closest = temp
                third_closest = temp2
                row_num1 = row["station_id"]
                row_name1 = row['name']
            elif (first_closest < distance < second_closest) or second_closest == 0.00: #between 1st and 2nd
                third_closest = second_closest
                second_closest = distance
                #row_num2 = row_num1
                #row_name2 = row_name1
                row_num2 = row["station_id"]
                row_name2 = row['name']
            elif (second_closest < distance < third_closest) or third_closest == 0.00: #between 2nd and 3rd
                third_closest = distance
                row_num3 = row["station_id"]
                row_name3 = row['name']
            #print(first_closest, second_closest, third_closest)
        new_dict ={row_num1: row_name1, row_num2: row_name2, row_num3: row_name3}
        return new_dict



    def closest_bike(self, latitude, longitude):
        loaded_json = self.status.json()
        shortest_distance = 0
        new_dict = {}
        for row in loaded_json['data']['stations']:
            if row and "lat" in row.keys() and "lon" in row.keys():
                row_lat = float(row["lat"])
                row_lon = float(row["lon"])
                distance = self.distance(latitude, longitude, row_lat, row_lon)
                if distance < shortest_distance or shortest_distance == 0:
                    shortest_distance = distance # this is it chief
                    row_num = row["station_id"]
                    row_name = row['name']
        new_dict[row_num] = row_name
        return new_dict

        # return the station with available bikes closest to the given coordinates

    def station_bike_avail(self, latitude, longitude):
         loaded_json = self.status.json()
         new_dict = {}
         for row in loaded_json['data']['stations']:
             if row and "lat" and "lon" in row.keys():
                 row_lat = float(row["lat"])
                 row_lon = float(row["lon"])
                 if row_lat == latitude and row_lon == longitude:
                    row_id = int(row["station_id"])
                    loaded_other_json = self.response.json()
                    for rows in loaded_other_json['data']['stations']:
                        rows_id = int(rows["station_id"])
                        if rows_id == row_id:
                            row_num = int(rows["station_id"])
                            bike_num = int(rows['num_bikes_available'])
                            new_dict[rows["station_id"]] = bike_num
                            return new_dict
                        else:
                            new_dict = {}
         return new_dict

    def distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p)) / 2
        return 12742 * math.asin(math.sqrt(a))


# testing and debugging the Bike class

if __name__ == '__main__':
    instance = Bike('https://api.nextbike.net/maps/gbfs/v1/nextbike_pp/en', '/station_information.json', '/station_status.json')
    print('------------------total_bikes()-------------------')
    t_bikes = instance.total_bikes()
    print(type(t_bikes))
    print(t_bikes)
    print()

    print('------------------total_docks()-------------------')
    t_docks = instance.total_docks()
    print(type(t_docks))
    print(t_docks)
    print()

    print('-----------------percent_avail()------------------')
    p_avail = instance.percent_avail(342885) # replace with station ID
    print(type(p_avail))
    print(p_avail)
    print()

    print('----------------closest_stations()----------------')
    c_stations = instance.closest_stations(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_stations))
    print(c_stations)
    print()

    print('-----------------closest_bike()-------------------')
    c_bike = instance.closest_bike(40.444618, -79.954707)# replace with latitude and longitude
    print(type(c_bike))
    print(c_bike)
    print()

    print('---------------station_bike_avail()---------------')
    s_bike_avail = instance.station_bike_avail(40.444777, -80.000831) # replace with exact latitude and longitude of station
    print(type(s_bike_avail))
    print(s_bike_avail)
