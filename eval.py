#pylint: disable=no-member

"""
This .py file is used to evaluate the performance of the ANPR system.
It gets the average processing time of the system, the accuracy of OCR and saves the final images

"""



from scanner import PlateScanner
import os 
import config
import cv2
import numpy
import json
import numpy as np
import pathlib

def main():
    real_plates = json.loads(open("dataset.json", "r").read())

    times = []
    plates = []
    percentages = []
    
    cfg = config.check_config()
    if not cfg:
        exit()

    print("[N] \t\tTIME\tREAL\tREC\t\t ACC")

    for a in os.listdir("pdataset"): 
        if a.endswith(".jpg") or a.endswith(".png"):
            time, plate, end_img, plate_img = PlateScanner(f"pdataset/{a}",cfg).scan_plate()

            #create directory if it doesnt exist
            pathlib.Path("finalplates/plates").mkdir(parents=True, exist_ok=True)

            cv2.imwrite(f"finalplates/final_{a}", end_img)

            if not plate_img is None:
                cv2.imwrite(f"finalplates/plates/final_{a}", plate_img)

            ld, percent = get_ld(plate, real_plates[a])

            print(f"[{a}] \t{time}ms\t{real_plates[a]}\t{plate}\t\t levenshtein: {ld}\t\t{len(real_plates[a])-ld} / {len(real_plates[a])} {percent}%")

            #the system averages 140ms+ so if it is less than that then it means that the image has not been processed 
            #i.e. the plate has not been found
            if time > 100:
                times.append(time)

            plates.append(plate)
            percentages.append(percent)

    recognised_plates = []
    for b in plates:
        b = b.replace(" ", "")
        if b == "" or b == "NOPLATE":
            continue

        recognised_plates.append(b)

    mean, sd = calculate_performance(times)
    percent_mean, percent_sd = calculate_performance(percentages)
    print("\n\n", 20*"===", f"\nMEAN PROCESS: {round(mean,2)}ms\nPROCESS SD: {round(sd,2)}\nREC: {len(recognised_plates)}/{len(plates)} ({round(len(recognised_plates) / len(plates) * 100, 2)}%)\nACC: {round(percent_mean, 2)}%\nACC SD: {round(percent_sd, 2)}")

#calculates mean and standard deviation of a given list
def calculate_performance(list): 

    mean = numpy.mean(list, axis = 0)
    sd = numpy.std(list, axis = 0)

    end_list = [x for x in list if (x > mean - 2 * sd)]
    end_list = [x for x in end_list if (x < mean + 2 * sd)]
   
    return mean, sd

#gets levenshtein distance of two strings
#by comparing them and getting the amount of character insertions, deletions and substitutions

def get_ld(recognised, correct):
    m = len(recognised) 
    n = len(correct) 

    distance = []
    
    for i in range(m + 1):
        distance.append([i])
    
    for j in range(n+1):
        distance[0].append(j)
    
    for j in range(1,n+1):
            for i in range(1,m+1):
                if recognised[i-1] == correct[j-1]:
                    cost = 0           
                else:
                    cost = 1
                
                minimum = min(distance[i-1][j]+1, distance[i][j-1]+1, distance[i-1][j-1]+cost)         
                distance[i].insert(j, minimum)

    #ratio = round((((m+n) - distance[-1][-1]) / (m+n)) * 100, 2)
    ratio = round((1 - distance[-1][-1]/max(m, n)) * 100, 2)
    return distance[-1][-1], ratio

if __name__ == "__main__":
    main()