'''The implementation file for project 1 of Operations Management,
offered at PHBS in Peking University in 2020.
'''
#################################################################
#
# Team must implement this function for phase 1.

# The project in phase 1 is in an idealistic setting
# where the demand is simulated according to the
# mean and standart deviation by a normal distribution.

# The goal is to minimize the total inventory cost
# that consists of the order placing cost, the holding cost,
# and the stockout cost.

# Your policy will be scored by the total inventory costs
# in simulations with a randomly picked set of SKUs and
# randomly generated streams of daily demands after submission.

##################################################################
#
# Note: you may use external libraries that don't contain any
#       code or logic of inventory management, such as general
#       math libraries, graphing libraries, or statistics libraries.
#       Please list any external libraries used here,
#       and explain how to set them up so that your submission
#       can be tested successfully by the TA and teacher.
#
#
#
##################################################################

FILE_VERSION = "3.0" 


import numpy as np
import scipy.stats as st

def reorder_upto(sku_info, daily_demand, demand_stdev):
    '''Team must implement this function, which should
finish and return within *60 minutes* on a laptop.
If it exceeds 60 minutes, it will be terminated and
no results will be reported.

This is called in the beginning of simulation to obtain
an order-up-to policy which has two quantities:
  1. the reorder point. and 2. the replenishment level.
In the beginning of every day, the policy is applied
to the current inventory position in the simulation.

@arguments:
    sku_info: an instance of SKU_Info class in p1test.py.
              Please refer to the code for class SKU_Info
              in p1test.py for more information.
        * You may refer to the data file for values.

    daily_demand: the average daily demand.
              
    demand_stdev: the standard deviation of the daily demand.

@returns:
    return a tuple of two integers:
          the reorder point and the replenishment level,
          in that order, as shown in the code below.
          These 3 lines of code are only for illustration,
          you may delete and write your own.
          When you write your own code, please use intuitive
          names for your variables for better readability.
'''
# These names are adopted from the book
    print('\nWe are currently testing with the SKU denoted as\t' ,sku_info.SKU)
    print('\n\tIts lead time is: \t\t\t\t', round(sku_info.lead_time_days,3))
    print('\tIts unit cost is around: \t\t\t', round(sku_info.unit_cost,3))
    print('\tIts unit profit is around: \t\t\t', round(sku_info.unit_profit,3))
    print('\tIts daily holding cost is around: \t\t', round(sku_info.holding_cost_day,3))
    print('\tIts cost per order is around: \t\t\t', round(sku_info.cost_per_order,3))
    print('\tIts stockout cost is around: \t\t\t', round(sku_info.stockout_cost, 3))

    # Rename the values from the inputs
    d = daily_demand
    stdev = demand_stdev
    L = sku_info.lead_time_days
    M = sku_info.stockout_cost
    H = sku_info.holding_cost_day
    S = sku_info.cost_per_order

    # see if the inputs meet the approximation criteria
    approximation_criteria = round(stdev/d, 1)
    
    if approximation_criteria <=2:
      print(f'\nIts Demand does not vary very much (stdev/d is close to {approximation_criteria}). Therefore the approximation on ppt p.55 can be applied.\n')
    else:
      print('\nIts demand varies significantly. The decisions might not be optimal.\n')
    
    # calculating Z value with optimal service level formula
    if M > 0 and (M/H)>np.sqrt((2*np.pi)) :
    # there are products with negative profit, also the optimal service level requires M/H>sqrt(2*pi)
      
      numerator = M
      denominator = np.sqrt(2*np.pi) * H * L

      Z = np.sqrt(2 * np.log(numerator/denominator))
      
      # the formula for the safety stock is the one for the model with varying demand and fixed time
      ss = Z * stdev * np.sqrt(L)

      print('\tThe Z value is set to be around:', round(Z,3))

    else:
      ss = stdev * np.sqrt(L)

    # safety stock = Z * stdev, from book p. 511
    print('\tIts safety stock is around: \t\t\t', int(ss))

    # get the integer value of reorder_point
    reorder_point = int(ss + d * L)

    # Caluculate Q*, supposing there are 250 working days in a year
    EOQ=np.sqrt(2*250*d*S/H/365)
    print('\tThe EOQ is:', int(EOQ))
    
    n = int(d*L/EOQ+1)
    #find the optimal integer
    replenishment_level = int(ss+ n * EOQ)
    
    print(f'\nThe decisions for the SKU {sku_info.SKU} have been made:')
    print(f'\n\tThe reorder point is: \t\t{reorder_point}' )
    print(f'\tThe replenishment_level is: \t{replenishment_level}')
      
    return reorder_point, replenishment_level


#############################################################
## NOTICE: the code below this line is NOT used in phase 1 ##
#############################################################





###########################
### PHASE 2 starts here ###
###########################

################################################
#Team must implement this function for phase 2.#

# The project in phase 2 is in a more realistic setting
# where the demand is taken from history demand records
# of a real business. You will be given some SKUs and
# their demand data to test your policy by your own.

# The goal is to minimize the total inventory cost
# that consists of the order placing cost, the holding cost,
# and the stockout cost.

# Your phase 2 submission will be evaluated against
# a randomly picked set of SKUs with their demand history.

import math # since 2.0
def initialize(sku_info, history, current_ip, ctx): # since 2.0
    '''This function is called only once before order_decision(...)
starts to be called once a day. You can save whatever states in ctx,
for example, the number of days passed, a tracking signal, etc.'''
    # these states are for a tracking signal
    ctx.days = 0
    ctx.error_sum = 0.0
    ctx.SAD = 0.0 #sum of absolute deviation
    # for alternatives: https://en.wikipedia.org/wiki/Tracking_signal

import statistics as stats

def order_decision(sku_info, history, current_ip, ctx):
    '''Team must implement this function, which should
finish and return within *10 second* on *average* on a laptop.

This is called in the beginning of everyday
to decide on the extra units to order from supplier.

To be more specific, this function will be called on 360 days
to execute your policy on a SKU, therefore the total amount
of time used by your function should not exceed 3600 seconds,
which is exactly 1 hour. If it exceeds one hour, it will be
terminated and no results will be reported.

It is guaranteed that demand_history will contain a history
for at least 60 most recent days.

@arguments:
    sku_info: an instance of SKU_Info class in p1test.py.
              Please refer to the code for class SKU_Info
              in p1test.py for more information.
        * You may refer to the data file for values.

    history: a list of daily demand from the recent past,
              e.g. demand_history[-1] is the demand of yesterday,
              demand_history[-2] is the demand of the day before
              yesterday, and so on so forth.
              Note: Do NOT try to modify the demand history.
              
    current_ip: the current inventory position
              (inventory in stock + inventory on the way)

@returns:
    return 0 if there is no need to order anything, otherwise
    return a positive integer as the number of units to order.
'''
    history = history[-60:] # discard data more than 60 days old
    mean = stats.mean(history)
    stdev = stats.stdev(history, mean)
    reorder_point = int((mean+ stdev) * sku_info.lead_time_days)

    # suppose history[-2] is the forecast for history[-1], update MAD, and error_sum
    ctx.SAD = ctx.SAD + math.fabs(history[-1]-history[-2]) # since 2.0
    ctx.error_sum += history[-1]-history[-2] # since 2.0
    ctx.days += 1 # since 2.0
    if ctx.SAD > 0: # since 2.0
        tracking_signal = ctx.error_sum * ctx.days/ctx.SAD # since 2.0
        #print(f"Tracking signal: {tracking_signal}")

    # # These names are adopted from the book
    # print('\nWe are currently testing with the SKU denoted as\t' ,sku_info.SKU)
    # print('\tIts daily demand is:\t\t\t\t' ,mean)
    # print('\tIts lead time is: \t\t\t\t', round(sku_info.lead_time_days,3))
    # print('\tIts unit cost is around: \t\t\t', round(sku_info.unit_cost,3))
    # print('\tIts unit profit is around: \t\t\t', round(sku_info.unit_profit,3))
    # print('\tIts daily holding cost is around: \t\t', round(sku_info.holding_cost_day,3))
    # print('\tIts cost per order is around: \t\t\t', round(sku_info.cost_per_order,3))
    # print('\tIts stockout cost is around: \t\t\t', round(sku_info.stockout_cost, 3))

    # Rename the values from the inputs
    d = mean
    stdev = stdev
    L = sku_info.lead_time_days
    M = sku_info.stockout_cost
    H = sku_info.holding_cost_day
    S = sku_info.cost_per_order

    # Uncomment to see if the inputs meet the approximation criteria
    # if d != 0:
    #   approximation_criteria = round(stdev/d, 1)

    #   if approximation_criteria <=2:
    #     print(f'\nDemand does not vary very much (stdev/d is close to {approximation_criteria}). Therefore the approximation on ppt p.54 can be applied.\n')
    #   else:
    #     print('Demand varies significantly. The decisions might not be feasible.\n')
    # else:
    #   print('Average demand for the first 60 days were 0!')
    
    
    
    # calculating Z value with optimal service level formula
    if M > 0 and (M/H)>np.sqrt((2*np.pi)) :
    # there are products with negative profit, also the optimal service level requires M/H>sqrt(2*pi)
      numerator = M
      denominator = np.sqrt(2*np.pi) * H * L
      Z = np.sqrt(2 * np.log(numerator/denominator))
      
      # the formula for the safety stock is the one for the model with varying demand and fixed time
      ss = Z * (d+stdev) * np.sqrt(L)

      # print('\tThe Z value is set to be around:', round(Z,3))

    # else assume Z =1 
    else:
      ss = stdev * np.sqrt(L)

    # safety stock = Z * stdev, from book p. 511
    # print('\tIts safety stock is around: \t\t\t', int(ss))

    # get the integer value of reorder_point
    reorder_point = int(ss + d * L)

    # Caluculate Q*, supposing there are 250 working days in a year
    EOQ=int(np.sqrt(2*250*d*S/H/365))
    # print('\tThe EOQ is:', EOQ)
    
    replenishment_level = EOQ
    i=0
    while i<5: 
      if replenishment_level < reorder_point:
          replenishment_level += 12*EOQ
          i+=1
      else:
        break
    
    if replenishment_level< reorder_point:
      replenishment_level = reorder_point


    # print(f'\nThe decisions for the SKU {sku_info.SKU} have been made:')
    # print(f'\n\tThe reorder point is: \t\t{reorder_point}' )
    # print(f'\tThe replenishment_level is: \t{replenishment_level}')
    # print()

    return 0 if current_ip > reorder_point else replenishment_level - current_ip

