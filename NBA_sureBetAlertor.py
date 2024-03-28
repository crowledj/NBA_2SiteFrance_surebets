import random
from bs4 import BeautifulSoup
import re
import smtplib
import time
#strtime_file = time.time()
import timeit
from collections import defaultdict
from smtplib import SMTPException
import re,pprint

#import requests
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException, TimeoutException

from selenium.webdriver.support.ui import Select

from selenium.webdriver.chrome.options import Options
import itertools
import sys,os
#from scraper_api import ScraperAPIClient
import datetime, unidecode
import subprocess
#from googletrans import Translator

# init the Google API translator
#translator = Translator()

from webdriver_manager.chrome import ChromeDriverManager

## turn down level of v verbose by dwfauklt selenium webdriver logging , lol
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.service import Service
import copy

#create a global random waitimte to reuse in the scraping further on..
wait_time12 = random.randint(1,2)


# set aws CLI creds using boto here:
#import boto3	
#client = boto3.client('sns','ca-central-1')
#store Paul Darmas's number:
my_phone_number          = '0014372468105'
main_client_phone_number = '0033609590209'
courrouxbro1_client_phone_number = '0033647228992'
courrouxbro2client_phone_number  = '0033620858827'
# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)

sys.path.append('./')
from metaLeague_data import *

# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)
surebet_factor = 1.0
#cibstant initialised to False - for determining if they customer's expected odds are retrieved for alert system...
odd_are_found = False
TEST_MODE = False

DEBUG_PRINTS=True

list_mailed_surebets = []

full_all_bookies_allLeagues_match_data_copy = {}

# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
# req_proxy = RequestProxy(log_level=logging.ERROR) #you may get different number of proxy when  you run this at each time

# if not TEST_MODE:
#     proxies = req_proxy.get_proxy_list()
def check_is_surebet(*args): 

    total_iverse_odds_sum = 0.0
    for odds in args:
        #print('in check_is_surebet() func. --  odds_i = ' + str(odds) + ' ')
        if odds == 0:
            pass
        else:
            total_iverse_odds_sum += 1/(odds)

    #
    #print(' Surebet value = ' + str(total_iverse_odds_sum))

    if total_iverse_odds_sum < 1.0 and total_iverse_odds_sum > 0.0:
        return True

    return False    

def get_surebet_factor(*argv): #  odds_A, odds_B):

    global surebet_factor

    if len(argv) >= 1:
    # reset this global value -- but must think on should I create class 'gambler' to correctly initialise these kinds of vars and update per instance etc..(?)
        surebet_factor = 0.0

        #total_iverse_odds_sum = 0.0
        for odds in argv:
            if odds == 0.0:
                pass
            else:
                surebet_factor += 1/(odds)

    #print('in get surebet function -- surebet = ' + str(surebet_factor))

    return surebet_factor


def return_surebet_vals(*argv, stake):  #odds_A, odds_B,stake):

    surebetStakes = []

    # !! NoTE : ive added a '100.0' factor into the calculations below to display to the lads in their emails
    for i,odds in enumerate(argv):

        if odds == 0.0 or surebet_factor == 0.0 :
            surebetStakes.append(1)
        else:    
            surebetStakes.append((1/surebet_factor)*(1/odds))
            #print('surebetStakes[' + str(i) + '] =  ' + str(surebetStakes[i]))

    return surebetStakes


## TODO : must generalize this and add file to code bundle
DRIVER_PATH = 'chromedriver' #the path where you have "chromedriver" file.

options = Options()
options.headless =  False #True
#options.LogLevel = False
options.add_argument("--window-size=1920,1200")
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")
#driver = webdriver.Chrome(options=options) #, executable_path=DRIVER_PATH, service_args=["--verbose", "--log-path=D:\\qc1.log"])


def check_for_sure_bets(*args):

    global all_split_sites_data, DEBUG_OUTPUT, globCounter

    # init. copy data dict.
    all_split_sites_data_copy = {}
    dont_recimpute_surebets = False  

    returnBetSizes = False
    stake_val      = 1.0  #(euro)  
    if len(args) > 0 :
        stake_val      = args[0]    
        returnBetSizes = True

    # initialize proxy count and create list of proxies from the prox generator
    # PROXY_COUNTER = 0
    # k = 33
    # proxies = req_proxy.get_proxy_list()

    # ## TEST
    # proxies = proxies[:100]
    ##end test

    #initialize counters
    sure_bet_counter = 0
    total_time_parsing = 0.0
    globCounter=0
    dataDictChangdCounter = 0

    while(True):

        # if PROXY_COUNTER >= len(proxies) - (2*RAND_PROXY_JUMP + 1):
        #     proxies = req_proxy.get_proxy_list()
        #     PROXY_COUNTER = 0
        # PROXY = proxies[PROXY_COUNTER].get_address()
        #print("Proxy address = ******************************** %s ************************************ %d",PROXY,k)
        
        driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install())) #, executable_path=DRIVER_PATH)

        # webdriver.DesiredCapabilities.CHROME['proxy']={
        #     "httpProxy":PROXY,
        #     "ftpProxy":PROXY,
        #     "sslProxy":PROXY,
        #     "proxyType":"MANUAL",
        # }
        # PROXY_COUNTER += random.randint(1,RAND_PROXY_JUMP)
        # k += 1
        
        #endtime_file = time.time()
        #print('time to get to parsing was = ' + str(endtime_file - strtime_file))
        #print('Click on the "esc" key @ any time to terminate this program and can then restart again any time you wish :) ......')
        # waitr a delay time to refresh sites parsings....
        start_parse = time.time() 

        start_full_parsingTimer = time.time()
        try:
            parseSites(driver) #, input_sports, input_competitions): #all_srpaed_sites_data):
            end_parse = time.time() 
            print('Time to do parsing was = ' + str(end_parse - start_parse))
            total_time_parsing += (end_parse - start_parse) 
            pass

        except Exception as e:
            print("Error in parsing function...retrying... But needs diagnostics and/or a fix ! ...")
            continue

        # print('********************************************************************************print  ******************************************************************************** ')   
        # print(' ******************************************************************************** OLD Dict : ********************************************************************************')
       
        # print(str(all_split_sites_data_copy))
        # print(' ############################################################################### OLD Dict : FOINISHED   ###############################################################################')
        # print('lenght of old dict = ' + str(len(all_split_sites_data_copy)))
        
        globCounter += 1
        if all_split_sites_data == all_split_sites_data_copy:
            dont_recimpute_surebets = True
            dataDictChangdCounter += 1
            print(' #############################################################new data dict. has NOT been updated ...:( -- so no need to re-check surebets        ################################################################### .... ;)')
            time.sleep(1)
        else:
            dont_recimpute_surebets = False
            # print('lenght of NEWd dict = ' + str(len(all_split_sites_data)))
            print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&  new data dict. has been updated ...:( -- so can check surebets .. %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% .... ;)')
            
        print('total num attempts/loops  = ' + str(globCounter) + '-- no. of times data changes & was updated in parsing = ' + str(globCounter - dataDictChangdCounter))    
            #print('###############################################################################  Current Dict : ')
        
            # print(str(all_split_sites_data))
            # print(' ############################################################################### Current Dict FINISHED  ###############################################################################')
            # #print('new data dict. has been updated ...! :)')

    ## print average timers  parsings of each sites:
        #print('AVerage time to do cbet parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_cbet/globCounter))
        print('AVerage time to do piwi parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_unibet/globCounter))
       
        print('AVerage time to do betclic parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_betclic/globCounter))

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

        #local copy in infinite loop to check if its changed or not - then dont need to redo sure bets checks if not
        all_split_sites_data_copy = copy.deepcopy(all_split_sites_data)

        wait_time = random.randint(1,2)
        time.sleep(wait_time)   
        if len(all_split_sites_data) < 2 :
            print('*************************** Error - less than three bookies scrapped for games here ..., try again -- if this error persists raise a bug ******************************')
            #return False            
            continue    

    #    /\ if (globCounter % 5) == 0:
        print('AVerage time to do parsings was = ' + str(total_time_parsing/globCounter)) 
        print('number of surebets found so far is = ' + str(sure_bet_counter))    

        if not dont_recimpute_surebets :
            start_surebet_timer = time.time()
            index = 0    
            ## TODO  - a biggg TODO  -- the following is just the combos of 3 but will also need to cater for when only 2 bookies are involved in a footy surebet :
            # i.e 1 bookie has the needed home win and draw odd and the other the awat=y win and also vice versa.
            #redundancy_bet_checklist = {}

            checxking_surebet_counts = 0
            for subset in itertools.combinations(all_split_sites_data, 2):  
                #filter unique games across dicts/sites using the key from a fixed one ....  
                #                
                subsetList = list(subset)         
                index += 1 

                if ( len(subsetList) >= 2):
                    second_bookie_keys = subsetList[1].keys() 
                    third_bookie_keys  = subsetList[2].keys()         

                bookie_2 = ''
                for keys in second_bookie_keys:
                    bookie_2 = keys.split('_')[0]
                    break   

                if len(subsetList) >= 2:    
                    for key in subsetList[0]:    

                        key_str_split_by_underscore = key.split('_')    
                        if len(key_str_split_by_underscore) >= 4:

                            bookie_1 = key_str_split_by_underscore[0]
                            #local_bookies_list.append(bookie_1)
                            date_1 =   key_str_split_by_underscore[1]
                            competition_1 = key_str_split_by_underscore[2]
                            sub_key_str_split_by_underscore = key_str_split_by_underscore[-1].split(' - ')
                            sub_key_str_split_by_space = key_str_split_by_underscore[-1].split(' ')
                            sub_key_str_split_by_vs = key_str_split_by_underscore[-1].split(' vs ')

                            if len(sub_key_str_split_by_underscore) != 2:
                                if len(sub_key_str_split_by_space) != 2:
                                    sub_key_str_split_by_works = sub_key_str_split_by_vs
                                else:
                                    sub_key_str_split_by_works = sub_key_str_split_by_space    
                            else:
                                sub_key_str_split_by_works = sub_key_str_split_by_underscore        

                            if len(sub_key_str_split_by_works) >= 2:
                                teamA_1 =  sub_key_str_split_by_works[0]
                                teamB_1 =  sub_key_str_split_by_works[1]       

                        unique_math_identifiers = [competition_1,teamA_1,teamB_1]

                        if DEBUG_OUTPUT :
                            print('site_data key = ' + str(key) )

                        matching_keys2_list = []
                        key_bookkie2 = 'void2'
  
                        truth_list_subStrKeysDict2 = [matching_keys2_list.append(key2) for key2,val in subsetList[1].items() if (unique_math_identifiers[0] in key2 and unique_math_identifiers[1] in key2 and unique_math_identifiers[2] in key2)]

                        if len(truth_list_subStrKeysDict2) > 0:
                            key_bookkie2 = matching_keys2_list[0]
   
                        if (truth_list_subStrKeysDict2 and not (find_substring(bookie_1,bookie_2) )):
                            
                            checxking_surebet_counts += 6
                            home_win_odds, away_win_odds = subsetList[0][key][0], subsetList[1][key_bookkie2][1]
                            #print('\n \n')

                            if  check_is_surebet(home_win_odds, away_win_odds):  # encode bookie outcomes as 'W','D','L' wrt to the 1st team in the match descrpt. , i.e The 'hometeam' 
                                
                                # if  returnBetSizes:
                                sure_bet_counter += 1
                                print('***********************************************************************************************************************************************************************************')   
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************')   
                                print('***********************************************************************************************************************************************************************************')   

                                print('Odds comboo is')
                                print(W_1)
                                print(D)
                                ## as odds are 0,1 from 1st two bookies

                                stake = 100.0
                                get_surebet_factor(home_win_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0                                   

                                proportionsABC_list =  return_surebet_vals(home_win_odds, away_win_odds,stake = stake)


                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds)

                                continue

                            home_win_odds, away_win_odds = subsetList[0][key][0], subsetList[1][key_bookkie2][2]
                            if  check_is_surebet(home_win_odds, away_win_odds):

                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************') 
                                # given the last indices are 2,1,0
                                # W_1,W_2
                                ## calc. % profit for the lads:
                                stake = 100.0
                                get_surebet_factor(home_win_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0 
                                
                                #get_surebet_factor(subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                #vg_profit = round((1/3)*(profit_1 + profit_2 + profit_3),3)                                

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_1,W_2,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  sombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the away win at odds = '  + str(subsetList[1][key_bookkie2][2]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' + str(subsetList[2][key_bookkie3][1]) + str(bookie_3) + '  \n')
                                #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]],1000)
                                continue
                else:
                    print("Not enough bookies scraped correctly to look for 3 - way surebets...")
            print('NO. surebets possibilities checked = ' + str(checxking_surebet_counts))        
        if not dont_recimpute_surebets:
            end_surebet_timer = time.time()
            print("Time taken to just check for surebets besides parsing = " + str(end_surebet_timer - start_surebet_timer))

    return True

#if only soing 2 - way sure bet , then oddDraw can be set to -1 and used as such when read in here
def send_mail_alert_odds_thresh(win_lose_or_draw,expect_oddB,actualOdd,teamA,teamB,date,competition,bookiesNameEventB):

    global DEBUG_OUTPUT
    successFlag = False
    sender = 'godlikester@gmail.com'
    receivers = ['crowledj@tcd.ie'] #,'pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com']

    # message = """From: From Person <from@fromdomain.com>
    # To: To Person <to@todomain.com>
    # Subject: SMTP e-mail test

    # The is an Alert to tell you that a three-way soccer sure bet exists between --""" + str(teamA) + """ and  """ + str(teamB) + """  in the event """ + str(competition) + """  \
    # on the date  """ + str(date) + """  the bet will involve placing a bet on """ + str(bookie_one_outcome) + """  in the bookies - """ + str(bookie_1) + """ and on the outcome """ \
    # + str(bookie_2_outcome) + """ in the """ + str(bookie_2) +  """ bookie and final 3rd bet left in  """ + str(bookie_3)

    bookieTeamA = ""
    bookieTeamB = ""
    bookieDraw  = ""

    if "Home team " in bookie_one_outcome:
        bookieTeamA = bookie_1
    elif  "Away team " in bookie_one_outcome:
        bookieTeamB = bookie_1  
    else:
        bookieDraw = bookie_1      
   
    if "Home team " in bookie_2_outcome:
        bookieTeamA = bookie_2
    elif  "Away team " in bookie_2_outcome:
        bookieTeamB = bookie_2  
    else:
        bookieDraw = bookie_2


    if  bookieTeamA == "":
        bookieTeamA = bookie_3

    elif bookieTeamB == "":
        bookieTeamB = bookie_3     

    else:
        bookieDraw = bookie_3 


    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    Surebet Alert 
      
    Event: """ + str(competition) + """
    Date: """ + str(date) + """
    teamA: """ + str(teamA) + """
    teamB: """ + str(teamB) + """

    bookieTeamA: """ + str(bookieTeamA) + """
    bookieDraw: """  + str(bookieDraw) + """
    bookieTeamB: """ + str(bookieTeamB) 

    print(' ********************   message = ' + message)
    print(' ******************** ')

    try:
        smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
        smtpObj.login("godlikester@gmail.com", "Pollgorm1")
        smtpObj.sendmail(sender, receivers, message)     

        if DEBUG_OUTPUT :
            print("Successfully sent email")

        successFlag = True
    except SMTPException:
        print("Error: unable to send email")
        pass

    return successFlag

def send_mail_alert_gen_socer_surebet_prportions( teamA, teamB, date, proportionsABC_listRnd, Profit, betclic_odds, piwi_odd, betclic_home_switch):

    global DEBUG_OUTPUT, surebet_factor
    successFlag = False
    sender =  'crowledj@tcd.ie'#'godlikester@gmail.com'

## TEST - ONLY HARDCODING HERE FOR FIRST KNCK OUT RUN OF CHAMPIONS LEAGUE GAMES
    #competition = 'Ligue des Champions'
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!! END TEST !!!!!!!!!!!!!

    if TEST_MODE:
        receivers = ['crowledj@tcd.ie'] 
    else:
        receivers = ['godlikester@gmail.com', 'crowledj@tcd.ie', 'raphael.crx@gmail.com', 'corentin.51mathieu@gmail.com' ] #'raphael.courroux@hotmail.fr'
    message = """From: From Dave Crowley>
    To: Corroux Bros
    Subject: Alert - Surebet found """

    bookieTeamA = ""
    bookieTeamB = ""

    if betclic_home_switch :
        bookieTeamA           = 'Betclic'
        proportions_list_win  = proportionsABC_listRnd[0]
        winOdd                = betclic_odds

        bookieTeamB           = 'Piwi24'  
        proportions_list_lose = proportionsABC_listRnd[1]
        loseOdd               = piwi_odd

    else:

        bookieTeamA         = 'Piwi24'  
        proportions_list_win = proportionsABC_listRnd[1]
        winOdd               = piwi_odd

        bookieTeamB           = 'Betclic'  
        proportions_list_lose = proportionsABC_listRnd[0]
        loseOdd               = betclic_odds        
 

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    Surebet Alert  :

    Profit = """ + str(round( Profit, 2)) + """
      
    Event: """ + "NBA" + """
    Date: """  + str(date) + """
    teamA: """ + str(teamA) + """
    teamB: """ + str(teamB) + """

    bookieTeamA: """ + str(bookieTeamA) + """   """  +  str(round(proportions_list_win  *100.0,2)) + """ % -- odd_1 is = """  +  str(winOdd)  + """        
    bookieTeamB: """ + str(bookieTeamB) + """   """  +  str(round(proportions_list_lose *100.0,2)) + """ % -- odd_3 is = """  +  str(loseOdd)     

    print(' ********************   message = ' + message)
    print(' ******************** ')
 
    if Profit > 0.15:

        try:
            smtpObj = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            smtpObj.login("crowledj@tcd.ie", "Elnino_9")

            #smtpObj.login("godlikester@gmail.com", "Pollgorm1")
            #smtpObj.login("keano16@dcrowleycodesols.com", "Pollgorm9")
            smtpObj.sendmail(sender, receivers, message)         
            print("Successfully sent email")

            successFlag = True
        except SMTPException:
            print("Error: unable to send email")
            pass

    return successFlag, [bookieTeamA, bookieTeamB], [proportions_list_win, proportions_list_lose], [winOdd, loseOdd]  


def send_mail_alert_gen_socer_surebet(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,date,competition):

    global DEBUG_OUTPUT
    successFlag = False
    sender = 'godlikester@gmail.com'
    receivers = ['crowledj@tcd.ie','pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com','scourroux@hotmail.com']

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test"""

    bookieTeamA = ""
    bookieTeamB = ""
    bookieDraw  = ""

    if "Home team " in bookie_one_outcome:
        bookieTeamA = bookie_1
    elif  "Away team " in bookie_one_outcome:
        bookieTeamB = bookie_1  
    else:
        bookieDraw = bookie_1      
   

    if "Home team " in bookie_2_outcome:
        bookieTeamA = bookie_2
    elif  "Away team " in bookie_2_outcome:
        bookieTeamB = bookie_2  
    else:
        bookieDraw = bookie_2


    if  not bookieTeamA :
        bookieTeamA = bookie_3

    elif not bookieTeamB :
        bookieTeamB = bookie_3     

    else:
        bookieDraw = bookie_3 


    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    Surebet Alert 
      
    Event: """ + str(competition) + """
    Date: """ + str(date) + """
    teamA: """ + str(teamA) + """
    teamB: """ + str(teamB) + """

    bookieTeamA: """ + str(bookieTeamA) + """
    bookieDraw: """  + str(bookieDraw) + """
    bookieTeamB: """ + str(bookieTeamB)

    print(' ********************   message = ' + message)
    print(' ******************** ')
    if message in list_mailed_surebets:
        print('sureBet already found -- dontt re-mail ')
        return successFlag

    try:
        smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
        smtpObj.login("godlikester@gmail.com", "Pollgorm1")
        smtpObj.sendmail(sender, receivers, message)         
        print("Successfully sent email")

        FP1 = open(surebets_Done_list_textfile,'a')
        FP1.write(message + '\n')
        FP1.close()

        successFlag = True
    except SMTPException:
        print("Error: unable to send email")
        pass

    return successFlag

tot_parionbet   = 0.0
tot_france_pari = 0.0
tot_winimax     = 0.0
tot_cbet        = 0.0
tot_pmu         = 0.0
tot_unibet      = 0.0
tot_betclic     = 0.0

league_or_cup_name = "MLs"  
compettition = "reg_competition"
def parseSites(driver): #, input_sports, input_competitions ): 

    start_mainParserTimer = time.time()
    global websites_champs_league_links, compettition, date, refernce_champ_league_gamesDict, full_all_bookies_allLeagues_match_data, DEBUG_OUTPUT, all_split_sites_data, tot_parionbet , tot_france_pari, tot_winimax, tot_cbet, tot_pmu, tot_unibet, tot_betclic    

    # reset full league dict so as not to keep appending to it below
    full_all_bookies_allLeagues_match_data.clear()
    any_errors = True

    site_betclci_NBA_link = 'https://www.betclic.fr/basket-ball-s4/nba-c13'
                            #'https://www.betclic.com/en/sports-betting/basketball-s4/nba-c13'
    piwi_betfair_Basketball_link = "https://exch.piwi247.com/customer/sport/7522"

    #create a dictionary of all the 2023/24 NBA teams with the value being a potential shortened name for the team but the value being the actual full name in lower case letters:
    nba_teams_dict = {'Atlanta Hawks':'atlanta hawks','Boston Celtics':'boston celtics','Brooklyn Nets':'brooklyn nets','Charlotte Hornets':'charlotte hornets','Chicago Bulls':'chicago bulls','Cleveland Cavaliers':'cleveland cavaliers','Dallas Mavericks':'dallas mavericks','Denver Nuggets':'denver nuggets','Detroit Pistons':'detroit pistons','Golden State Warriors':'golden state warriors','Houston Rockets':'houston rockets','Indiana Pacers':'indiana pacers','Los Angeles Clippers':'los angeles clippers','Los Angeles Lakers':'los angeles lakers','Memphis Grizzlies':'memphis grizzlies','Miami Heat':'miami heat','Milwaukee Bucks':'milwaukee bucks','Minnesota Timberwolves':'minnesota timberwolves','New Orleans Pelicans':'new orleans pelicans','New York Knicks':'new york knicks','Oklahoma City Thunder':'oklahoma city thunder','Orlando Magic':'orlando magic','Philadelphia 76ers':'philadelphia 76ers','Phoenix Suns':'phoenix suns','Portland Trail Blazers':'portland trail blazers','Sacramento Kings':'sacramento kings','San Antonio Spurs':'san antonio spurs','Toronto Raptors':'toronto raptors','Utah Jazz':'utah jazz','Washington Wizards':'washington wizards'}

    #expand this dictionary to include the shortened names (for eg. "NY Knicks" : "new york knicks" or 'Golden State':'golden state warriors') of the teams as the keys but with the same values:
    nba_teams_dict.update({'atlanta hawks':'atlanta hawks','boston celtics':'boston celtics','brooklyn nets':'brooklyn nets','charlotte hornets':'charlotte hornets','chicago bulls':'chicago bulls','cleveland cavaliers':'cleveland cavaliers','dallas mavericks':'dallas mavericks','denver nuggets':'denver nuggets','detroit pistons':'detroit pistons','golden state warriors':'golden state warriors','houston rockets':'houston rockets','indiana pacers':'indiana pacers','los angeles clippers':'los angeles clippers', 'los angeles lakers':'los angeles lakers', 'LA  lakers':'los angeles lakers', 'memphis grizzlies':'memphis grizzlies','miami heat':'miami heat','milwaukee bucks':'milwaukee bucks', 'minnesota timberwolves':'minnesota timberwolves','minnesota timb.':'minnesota timberwolves', 'minnesota timb':'minnesota timberwolves', 'new orleans pelicans':'new orleans pelicans','new york knicks':'new york knicks', 'NY knicks':'new york knicks', 'ny knicks':'new york knicks', 'oklahoma city thunder':'oklahoma city thunder','orlando magic':'orlando magic','philadelphia 76ers':'philadelphia 76ers','phoenix suns':'phoenix suns','portland trail blazers':'portland trail blazers','sacramento kings':'sacramento kings','san antonio spurs':'san antonio spurs','toronto raptors':'toronto raptors','utah jazz':'utah jazz','washington wizards':'washington wizards'})

    #update this dictionary to include other potential namings of the teams as the keys but with the same values, for example "NY Knicks" : "new york knicks", "LA raiders" : "Los Angeles Raiders" :
    nba_teams_dict.update({'atlanta':'atlanta hawks','boston':'boston celtics','brooklyn':'brooklyn nets','charlotte':'charlotte hornets','chicago':'chicago bulls','cleveland':'cleveland cavaliers','dallas':'dallas mavericks','denver':'denver nuggets','detroit':'detroit pistons','golden state':'golden state warriors','houston':'houston rockets','indiana':'indiana pacers','los angeles':'los angeles lakers','memphis':'memphis grizzlies','miami':'miami heat','milwaukee':'milwaukee bucks','minnesota':'minnesota timberwolves','new orleans':'new orleans pelicans','new york':'new york knicks','oklahoma':'oklahoma city thunder','orlando':'orlando magic','philadelphia':'philadelphia 76ers','phoenix':'phoenix suns','portland':'portland trail blazers','sacramento':'sacramento kings','san antonio':'san antonio spurs','toronto':'toronto raptors','utah':'utah jazz','washington':'washington wizards'})

    combined_leagues_maping = nba_teams_dict

    team_names_maping = combined_leagues_maping
    print('team_names_maping = ' + str(team_names_maping))
    print('in betclic ' +  league_or_cup_name  + ' pre-match parsing .... \n \n')
    
    global date_time 
    try:
        print('trying the driver.get on the new link....')
        driver.get(site_betclci_NBA_link)

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = True
        print("Error  caught in your BETCLIC initial website link .get.  --  retrying in while (true) inf loop :( .....")

    if any_errors:
        while any_errors:
            time.sleep(2)
            any_errors = False
            try:    
                driver.get(site_betclci_NBA_link)
                #driver.maximize_window()
            except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                any_errors = True
                print("Error  caught in your BETCLIC final rpound detect. func.  -- initial list games frabber  :( .....")
                continue                

    # grab the day/month/.year from today's date and store it
    todays_date = str(datetime.datetime.today()).split()[0] 
    date_time = str(datetime.datetime.today())

    comparison_substr = ' '
    try:

        time.sleep(wait_time12)
        # click accept button on popup
        ligue_1_finalrounds_list = driver.find_element("xpath", "/html/body/div/div/div[2]").click()

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = True
        print("Error  caught in your BETCLIC final rpound detect. func.  -- initial list games frabber  :( .....")  

    try:
        html = BeautifulSoup(driver.page_source,"html.parser")

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = True
        print("Error  getting the  html.parser:( .....")            

    try:

        innermost_element = html.find("app-desktop", class_="block").find("div",class_="layout").find("div",class_="layout_wrapper").find("bcdk-content-scroller", class_="content")
        #all_match_elements = innermost_element.find_all("sports-events-event", class_= "groupEvents_card ng-star-inserted")
        #grab only non lives events :
        non_live_panels = innermost_element.find_all("div", class_= "groupEvents")

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = True
        print("Error  getting the inner element from the initial html:( .....")          
        
    try:
        for panel_ in non_live_panels:
            if 'Maintenant' in panel_.text or 'Now' in panel_.text:
                continue

            all_match_elements = panel_.find_all("sports-events-event", class_= "groupEvents_card ng-star-inserted")
            for i, x in enumerate(all_match_elements):    
                #pass #print("\n The " + str0(i) + "th games text is...    ->   ");print(x[100:250]);i += 1;
                y = x.text.strip('\n')

                # find the odds for the home team and away team
                match_sub_str = re.split(r',', y)
                odd_home, odd_away = -1.0, -1.0
                if len(match_sub_str) >= 3:
                    if len(match_sub_str[0]) >= 1 and len(match_sub_str[1]) >= 2 and len(match_sub_str[2]) >= 2:
                        odd_home = float(match_sub_str[0][-1] + '.' +  match_sub_str[1][:2])
                        odd_away = float(match_sub_str[1][-1] + '.' +  match_sub_str[2][:2])
                
                if 'paris' in y:
                    indexes=find_substring("paris",y)
                else:
                    indexes = [0]*2
                    indexes[0]=0
                    indexes[1]=-1

                y_sniped_01 = y[indexes[0] + 5 : indexes[1]]
                y_sniped_01_lstrip_blnks = y_sniped_01.strip('\n')
        
                sub_strs_indxs = find_substring('\n ',y_sniped_01_lstrip_blnks)
                sub_space_caraige_strs_indxs = find_substring( ' \n',y_sniped_01_lstrip_blnks)

                left_indx = 0
                if len(sub_strs_indxs) >= 3:
                    left_indx = sub_strs_indxs[2]

                right_indx = -1 
                if len(sub_strs_indxs) >= 3:
                    right_indx = sub_space_caraige_strs_indxs[4]

                comparison_substr = y_sniped_01_lstrip_blnks[left_indx:right_indx]
                            
                # test method for removing all unwanted characters from the string found :
                # # initializing string
                test_str = comparison_substr #y_sniped_01_lstrip_blnks
                    
                # # initializing sub list
                sub_list = [" ", "\\n", "\+"]
                
                # Remove substring list from String using regex and join() function
                pattern = '|'.join(map(re.escape, sub_list))
                new_test_str = re.sub(r'\b(?:{})\b'.format(pattern), '', test_str)
                
                # printing result
                final_str = ' '
                k=0
                word_appemnder = []

                #comparison_substr_strip = comparison_substr.strip()
                for char in comparison_substr[0:-1]:
                    if '\\' not in char and '\\n' not in char and '\n' not in char and not char.isnumeric() and  '  ' not in char and  ':' not in char: 
                        k += 1
                        word_appemnder.append(char.lower())

                final_str = "".join(word_appemnder)
                last_stripd_date_no_time_stmp = unidecode.unidecode(final_str)

                print('odds info : Home odds = ' + str(odd_home) + " AWay odds = " + str(odd_away))

                last_stripd_date_no_time_stmp_strp      = last_stripd_date_no_time_stmp.strip()
                last_stripd_date_no_time_stmp_strp_splt = last_stripd_date_no_time_stmp_strp.split('-')
                team_A = last_stripd_date_no_time_stmp_strp_splt[0].rstrip()
                team_B = last_stripd_date_no_time_stmp_strp_splt[1].lstrip()

                print("Game info == :" + str(team_A) + " vs. " + str(team_B))

                full_all_bookies_allLeagues_match_data[ 'betclic'  + '_' + 'home' +  '-' + team_A + ':' + team_B ].append(float(odd_home)) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                full_all_bookies_allLeagues_match_data[ 'betclic'  + '_' + 'away' +  '-' + team_A + ':' + team_B].append(float(odd_away))

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = False
        print("Error getting the formatted  comparison string of the final match   :( .....")

    try:
   
        driver.get(piwi_betfair_Basketball_link)

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = True
        print("Error  caught in your Piwi initial website link .get.  --  retrying in while (true) inf loop :( .....")
        #continue

    if any_errors:
        while any_errors:
            x = random.randint(1, 3)
            time.sleep(x)

            any_errors = False
            try:    
                driver.get(piwi_betfair_Basketball_link)
            except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                any_errors = True
                print("Error  caught in your Piwi -- getting connected to initial NBA link... :( .....")
                continue

    if DEBUG_PRINTS:
        print(f"Connected to the piwi site but now -- grabbing the html of the site ...")    

    try:
        x = random.randint(1, 3)
        time.sleep(x)
        


        SCROLL_PAUSE_TIME = 1
        driver.execute_script("window.scrollTo(  " + str(0) +  ", "  + str(2) + "*document.body.scrollHeight);")
        last_height = driver.execute_script("return document.body.scrollHeight")

        time.sleep(2.5)    
        driver.execute_script("window.scrollTo(  " + str(2) +  ", "  + str(3) + "*document.body.scrollHeight);")

        # Wait to load page
        time.sleep(3*SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(2*SCROLL_PAUSE_TIME)

        y = random.randint(1, 3)
        time.sleep(y)
        html = BeautifulSoup(driver.page_source,"html.parser")

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = True
        print("Error  geconnecting to the piwi site imnitially with the driver.get() ( .....")
        #continue

    if DEBUG_PRINTS:
       print(f"GOT the html of the site successfully -- now going to try grab the rowContainers of the NBA matches  ...")    
    
    nba_panels_via_html = None
    try:
        x = random.randint(1, 3)
        time.sleep(x)

        time.sleep(1.5)    
        driver.execute_script("window.scrollTo(  " + str(0) +  ", "  + str(2) + "*document.body.scrollHeight);")

        # Wait to load page
        time.sleep(int(3*SCROLL_PAUSE_TIME))
  
        nba_panels_via_html = html.find_all("div", class_= "rowsContainer")
        time.sleep(1)

    except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
        any_errors = True
        print("Error  getting the  inner elements inside the html of PIWI - MUST FIIIXX !! ( .....")
        #continue

    if DEBUG_PRINTS:
        print(f"found html_rows and it = {nba_panels_via_html[-1].text}  ....")    

    found_NBA_panel = False
    nba_games_panel = None
    panel_index = -1
    for i, panel in enumerate(nba_panels_via_html):

        if 'In-Play' in panel.text or 'Q4' in panel.text or 'HT'  in panel.text or 'Q1' in panel.text or 'Q3' in panel.text:
            print('skippin the in play panel...')
            continue
        
        if DEBUG_PRINTS:
            print("going thru at start of panels search after in play check ..panel by panel with i = " + str(i) + "  ....")

        if found_NBA_panel:
            found_NBA_panel = False
            break
        
        if panel:

            nba_game_info = panel.text
            if nba_game_info:

                for key_, value in combined_leagues_maping.items():
                    if key_ in nba_game_info or value in nba_game_info:
                        found_NBA_panel = True
                        panel_index = i
                        break
                    else:
                        print("for the " + str(i) + " th panel -- no NBA panel found in the piwi247 website")
                        continue
    if DEBUG_PRINTS:                
        print("PAST  panels search after trying to assign 1st valid  and panel_index  = " + str(panel_index) + ", so now going through valid panels starting with this  ....")

    
    driver.execute_script("window.scrollTo(  " + str(0) +  ", "  + str(2) + "*document.body.scrollHeight);")

    x = random.randint(1, 3)
    time.sleep(x)

    for k, panel_ in enumerate(nba_panels_via_html[panel_index:]):
        team_names_elment = []
        for match in panel_:
            nonNBA_team_flag = False
            try:
                #x = random.randint(1, 3)
                #time.sleep(x)
                team_names_elment.append(match.find("div", class_="biab_market-title-cell styles_participantsNamesCell__kipAg").text)
                if DEBUG_PRINTS:
                    print(f'debug print -- AFTER  getting team_names_elment .... and it =  {team_names_elment[-1]}  ....')
                #print(team_names_elment[-1])

                if len(team_names_elment) != 0:
                    for Key, Value in team_names_maping.items():
                        if Key in team_names_elment[-1] or Value in team_names_elment[-1]:
                            nonNBA_team_flag = True
                            print(f'team name {team_names_elment[-1]} IS IN the team names mapping dictionary so conytiue onto processing it  processing...')
                            break
                        # else:
                        #     #nonNBA_team_flag = True
                        #     break
                    if not nonNBA_team_flag:
                        print(f'team name {team_names_elment[-1]} IS NOT IN the team names mapping dictionary so just Skip processing it...')
                        continue

            except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                any_errors = True
                print("Error  getting the first element inside the html of PIWI  :( .....")
                continue

            try:

                if DEBUG_PRINTS:
                    print(f'debug print -- at getting team_bets_elment_1   ....')
                team_bets_elment_1 = match.find("div",class_="styles_betContent__wrapper__25jEo")

                if DEBUG_PRINTS:
                    print(f'debug print -- AFTER  getting team_bets_elment_1 ....') # and it = {team_bets_elment_1}  ....')

                #print(team_bets_elment.text)
            except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                any_errors = True
                print("Error  getting the SECOND element inside the htam of PIWI - MU ( .....")
                continue

            try:
                # x = random.randint(1, 3)
                # time.sleep(x)

                if DEBUG_PRINTS:
                    print(f'debug print -- at getting blue-odds...')

                all_blue_odds = team_bets_elment_1.find_all("div", class_="styles_contents__Kf8LQ")

                if DEBUG_PRINTS and len(all_blue_odds) >= 1:
                    print(f'debug print -- AFTER getting bluereodds = ->{all_blue_odds[-1].text}<- ....')

            except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                any_errors = True
                print("Error  getting the THIRD element inside the htam of PIWI - MU ( .....")
                continue

            odd_home = -1.0
            odd_away = -1.0

            if DEBUG_PRINTS:
                print(f'debug print -- going through the  bluereodds& trying to get their text -and  odds....')

            try:
                time.sleep(2)
                if all_blue_odds and len(all_blue_odds) >= 3:
                # take care of the home odd
                    x = random.randint(1, 3)
                    time.sleep(x)
                    blue_odd_split_1 = all_blue_odds[0].text.split('.')
                    time.sleep(2)
                    if len(blue_odd_split_1) >=2:
                        time.sleep(1)
                        if len(blue_odd_split_1[1]) >= 2:
                            x = random.randint(1, 3)
                            time.sleep(x)
                            odd_home = float(blue_odd_split_1[0] + '.' + blue_odd_split_1[1][:2])
                    # if odd_home == -1.0:
                    #     continue
                    # else:
                    #     print(f'odd_home = {odd_home}')
                    # for the away odd
                    x = random.randint(1, 3)
                    time.sleep(x)
                    blue_odd_split_2 = all_blue_odds[2].text.split('.')
                    time.sleep(2)
                    if len(blue_odd_split_2) >=2:
                        time.sleep(1)
                        if len(blue_odd_split_2[1]) >= 2:
                            x = random.randint(1, 3)
                            time.sleep(x)
                            odd_away = float(blue_odd_split_2[0] + '.' + blue_odd_split_2[1][:2])
                        time.sleep(1)
                    # if odd_away == -1.0:
                    #     continue
                    # else:
                    #     print(f'odd_away_home = {odd_away}')                    

            except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException. IndexError) :
                any_errors = True
                print("Error  getting todds parsing in iw247 website - :( )")
                continue

            # if DEBUG_PRINTS:
            #     odd_home_ = str(odd_home)
            #     odd_away_ = str(odd_away)
                #print(f'DONE  going through the  bluereodds and done  trying to get their text -- hence the odds = {odd_home_} -- ....')
                #print(f'NOw filling the odds into the piwi dictionary ...')
                
            try:
                if len(team_names_elment) >= 1:
                    full_all_bookies_allLeagues_match_data[ 'piwi'  + '_' +  'away' +  ' - ' + unidecode.unidecode(team_names_elment[-1].lower())].append(odd_home) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ 'piwi'  + '_' + 'home' + ' - ' + unidecode.unidecode(team_names_elment[-1].lower())].append(odd_away)
                # elif len(team_names_elment) == 1:
                #     full_all_bookies_allLeagues_match_data[ 'piwi'  + '_' + team_names_elment[-1]].append(odd_home)
                else:
                    print('Error - no team names found in the piwi247 website')
                    continue

            except IndexError:
                print('Error - index error in creating and inserting into the overall main dict. !! ')
                continue

    if DEBUG_PRINTS:
        print(f'DONE filling the odds into the piwi dictionary and it = {str(full_all_bookies_allLeagues_match_data)} ...')

    # stop_mainParserTimer = time.time()
    global full_all_bookies_allLeagues_match_data_copy 
    if  full_all_bookies_allLeagues_match_data_copy == full_all_bookies_allLeagues_match_data:
        print('No new updated odds in the games found in the NBA games for today -- so exiting the program now...')
        return
    else:
        print('Updated odds found in the games in the NBA games for today -- so continuing the program now...')

    full_all_bookies_allLeagues_match_data_copy = copy.deepcopy(full_all_bookies_allLeagues_match_data)            
    betclic_home_odds,betclic_away_odds = -1.0, -1.0
    betclic_home_team, betclic_away_team = 'shite_utd', "crap_rovers"
    betclic__odds = -1.0
    betclic_home_switch = False
    date = str(datetime.datetime.today()).split()[0]
    for key_, val_ in full_all_bookies_allLeagues_match_data.items():
        #print('key = ' + str(key_) + '  ->  ' + str(val_))

        bookie_name, home_away_fullstr =  key_.split('_')

        teams_str = key_.split('-')[1]

        if bookie_name == 'betclic':
            betclic_home_team, betclic_away_team = teams_str.split(':')
            if 'home' in key_ and len(val_) > 0:
                betclic_odds = val_[0]
                betclic_home_switch = True
            else:
                betclic_odds = val_[0] 
        else:
            continue        
        
        home_away_str = home_away_fullstr[:4]

        for piwi_keys, piwi_vals in full_all_bookies_allLeagues_match_data_copy.items():

            if 'piwi' in piwi_keys:
                piwi_bookie_name, piwi_home_away_fullstr =  piwi_keys.split('_')
                piwi_teams_str = piwi_keys.split('-')[1]
                piwi_home_away_str = piwi_home_away_fullstr[:4]

                if ( betclic_home_team in piwi_teams_str.lower()  and betclic_away_team in piwi_teams_str.lower()) and home_away_str != piwi_home_away_str:

                    #print(f'in 1st 2 bookie odds email check...')
                    bookie_1 = 'Betclic'
                    bookie_2 = 'Piwi247'

                    teamA_1 = betclic_home_team 
                    teamB_1 = betclic_away_team
                    piwi_odd = piwi_vals[-1]
                    if betclic_home_switch:
                        away_win_odds = piwi_vals[-1]
                        home_win_odds = betclic_odds
                    else:
                        away_win_odds = betclic_odds
                        home_win_odds = piwi_vals[-1]

                    if  check_is_surebet(betclic_odds, piwi_vals[-1]):
                        #print(f'in checking surebet ...')

                        stake = 100.0
                        actual_profit = -100.0
                        surebet_factor = get_surebet_factor(betclic_odds, piwi_vals[-1])
                        if surebet_factor != 0.0 and surebet_factor != 0:
                            actual_profit = (((stake)/surebet_factor) - 100.0)/100.0
                        else:
                            actual_profit = 0.0 

                        proportionsABC_list =  return_surebet_vals(home_win_odds, away_win_odds,stake = stake)

                        proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                        
                        #send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, teamA_1, teamB_1, date,proportionsABC_listRnd, actual_profit, home_win_odds, away_win_odds)
                        # betclic_home_team='golden state warriors'
                        # betclic_away_team ='New york knicks'
                        # date='26/032024'
                        # proportionsABC_listRnd=[0.5,0.5]
                        # actual_profit=0.35
                        # betclic_odds=2.15
                        # piwi_odd=1.95
                        # betclic_home_switch=True
                        send_mail_alert_gen_socer_surebet_prportions(betclic_home_team, betclic_away_team, date, proportionsABC_listRnd, actual_profit, betclic_odds, piwi_odd, betclic_home_switch)
                                                                    #( teamA, teamB, date, proportionsABC_listRnd, Profit, betclic_odds, piwi_odd, betclic_home_switch)
                        print(f'Sent email to RAFA !!')
                

    #if  check_is_surebet(home_win_odds, away_win_odds):


    # print('Time to do main files full sites (8) parsing was = ' + str( stop_mainParserTimer - start_mainParserTimer ))
                        
    ## create sepaarate dicts for each bookies :
                        
    # create a list of the 20 most common girls names in the US
    #girls_names = ['Emma', 'Olivia', 'Ava', 'Isabella', 'Sophia', 'Mia', 'Charlotte', 'Amelia', 'Harper', 'Evelyn', 'Abigail', 'Emily', 'Elizabeth', 'Sofia', 'Madison', 'Avery', 'Ella', 'Scarlett', 'Grace', 'Chloe']

    unibet_dict      = defaultdict(list)
    piwi_dict        = defaultdict(list)


    driver.quit()
    return any_errors

if __name__ == '__main__':

    argv = sys.argv
    DEBUG_OUTPUT  = False
    print(' len(argv)  = ' + str(len(argv) ))


    retval2 = check_for_sure_bets()

    # if len(argv) >= 2 :

    #     if len(argv) == 8 :

    #         retVal = odds_alert_system(oddType= int(argv[1]), expect_oddValue= float(argv[2]), teamA= argv[3], teamB= argv[4], date= argv[5], competition= argv[6], Bookie1_used= argv[7], input_sports= [sports_btn_val], input_competitions = [compettition_btn_val])

    #     elif  len(argv) == 2 :

    #         retval2 = check_for_sure_bets() 

    #     else:

    #         #print("usage:  please indicate with  0 or a 1 in the first cmd line argument to the program wherether you wish to include debugging output prints in it's run or not; 0/1 corresponding to no/yes....")
    #         print("Usage : sportsbetAlertor_v1.py oddType (0 -home team win, 1 - a dra. 2 - away team win ) expect_soddValue teamA teamB competition Bookie1_used.    i.e 7 parameters on thye cmd line after the filename")
    #         print("Heres an Example --- sportsbetAlertor_v1.py  0 1.75  lyon  marseille  ligue1 Winamax")
    #         exit(1)
   
    # else:
    #     print("error found IN taking in cmd line args at start of program -- num args NOT >= 2")
    #     exit(1)

        #DEBUG_error foundOUTPUT = bool(int(argv[1]))
        #retval2 = check_for_sure_bets(input_sports= [sports_btn_val], input_competitions = [compettition_btn_val])   #sports_n_competetitons) #'unibet','zebet','winimaxc','W', 'D','marseilles','nantes','28/11/2020','ligue 1 UberEats')



#




