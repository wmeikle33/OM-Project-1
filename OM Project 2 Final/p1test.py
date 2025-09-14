#######################################################################
#
# This file is provided as a primitive tool for you to test your policy.
# You may want to further develop it to suit your needs,
#   but you will NOT submit this file.
#   You will only submit the p1team.py file for the project.
#   If your p1team.py depends on any other external code,
#   you must explain by comments in the beggining of p1team.py
#
#######################################################################
#
# Run this file as a python script:
#
# cmd> python p1test
#
# this will load your project program 'p1team.py'
# and the data files came with the project,
# to test your implementation.

FILE_VERSION = "3.0" #just in case we need to update

import logging
logging.basicConfig(
    # you may save message to a text file:
    #filename='testing.txt',
    # overwrite the messages in the text file
    #filemode='w', 
    format='%(levelname)s:%(message)s',
    #set level to logging.CRITICAL to suppress
    level=logging.CRITICAL) # logging.DEBUG 
def log_info(msg): logging.info(msg)



#consider loss of future businesses
STOCKOUT_PENALTY = 8.0

#the ratio of daily holding cost to unit cost
HOLDING_COST_RATIO = 0.2/360.0

class SKU_Info:
    '''
SKU_Info class that has these information about the SKU in question:

              sku_info.SKU: a string of the SKU code
              sku_info.lead_time_days: the lead time in days
              sku_info.unit_cost: the unit cost
              sku_info.unit_profit: the gross profit per unit
              sku_info.holding_cost_day: the holding cost/unit/day
              sku_info.cost_per_order: the fixed cost to place an order
              sku_info.stockout_cost: the cost for a unit of demand
                       experiencing stockout (future loss of demand from
                       the same customer, as well as platform policy
                       of reducing traffic and restricking orders on
                       frequent stockouts)

You may refer to the project data file for values of them.
'''
    __slots__ = ('SKU', 'unit_cost', 'unit_profit',
                 'lead_time_days', 'cost_per_order',
                 'holding_cost_day', 'stockout_cost')

    # NO.,SKU,Unit Cost,Gross Profit,Lead Time,Cost/Order
    def __init__(self, SKU, unit_cost, unit_profit,
                 lead_time_days, cost_per_order):
        self.SKU = SKU
        self.unit_cost = unit_cost
        self.unit_profit = unit_profit
        self.lead_time_days = lead_time_days
        self.cost_per_order = cost_per_order
        self.holding_cost_day = unit_cost * HOLDING_COST_RATIO
        #consider possible loss of future business
        self.stockout_cost = STOCKOUT_PENALTY * unit_profit

    def __repr__(self):
        return f'{self.SKU},{self.unit_cost},{self.unit_profit},{self.lead_time_days},{self.cost_per_order},{self.holding_cost_day},{self.stockout_cost}'

class Executor:

    def __init__(self, sku_info, initial_ip = 0):
        self.sku_info = sku_info
        # initial inventory position
        self.current_ip = initial_ip
        # initial inventory stock
        self.current_is = initial_ip

        self.ordering_cost = 0
        self.holding_cost = 0
        self.stockout_cost = 0
        self.order_queue = []
        self.day = 0

    def run_a_day(self, order_qty, todays_demand):
        assert order_qty >= 0
        self.day += 1
        log_info(f'run_a_day({order_qty}, {todays_demand}): day={self.day}, IS={self.current_is}, IP={self.current_ip}')

        # place order
        self.order_queue.append(order_qty)
        self.current_ip += order_qty
        if order_qty > 0:
            log_info(f'order placed: {order_qty}, IP: {self.current_ip}')
        
        # order arrival
        if len(self.order_queue)>self.sku_info.lead_time_days:
            arrived = self.order_queue[0]
            del self.order_queue[0]
            self.current_is += arrived
            if arrived > 0:
                log_info(f"order arrived: {arrived}, IS: {self.current_is}")
                
        log_info(f'current order queue: {self.order_queue}, total: {sum(self.order_queue)}')

        satisfied_demand = min(todays_demand, self.current_is)

        self.current_is -= satisfied_demand
        self.current_ip -= satisfied_demand

        if satisfied_demand > 0:
            log_info(f'demand satisfied = {satisfied_demand}')
            log_info(f'IS: {self.current_is}, IP: {self.current_ip}')

        # cost accumulations:
        if order_qty > 0:
            self.ordering_cost += self.sku_info.cost_per_order
            log_info(f'accumulated ordering cost: {self.ordering_cost:.2f}')

        holding_cost = self.sku_info.holding_cost_day * (
            self.current_is + satisfied_demand / 2. )
        self.holding_cost += holding_cost

        log_info(f'holding cost: {holding_cost:.2f}, accumulated: {self.holding_cost:.2f}')

        if todays_demand > satisfied_demand:
            stockout_cost = self.sku_info.stockout_cost * (
                todays_demand - satisfied_demand )
            self.stockout_cost += stockout_cost
            log_info(f'stockout cost: {stockout_cost:.2f}, accumulated: {self.stockout_cost:.2f}')

    def list_costs(self): # revised since 2.0
        return (self.ordering_cost + self.holding_cost + self.stockout_cost,
                self.ordering_cost, self.holding_cost, self.stockout_cost)

def phase1test(sku_info, daily_demand, demand_stdev, policy, rand, days=730):
    reorder_point, replenishment_level = policy(
            sku_info, daily_demand, demand_stdev)

    xx = Executor(sku_info, reorder_point + int(daily_demand+demand_stdev))
    
    for i in range(days):
        demand = int(rand.gauss(daily_demand, demand_stdev))+1
        if demand < 0: demand = 0
        if xx.current_ip <= reorder_point:
            order_qty = replenishment_level - xx.current_ip
        else: order_qty = 0
        xx.run_a_day(order_qty, demand)
        
    return xx.list_costs()

class PolicyContext: pass # since 2.0
def phase2test(sku_info, initial_ip, whole_demand_history, team_prog, days=360):
    assert len(whole_demand_history) >= 60 + days
    today = 61 #start from day 61
    demand_history = list(whole_demand_history[:today])
    frozen_history = frozenlist(demand_history)
    xx = Executor(sku_info, initial_ip)
    
    policy = team_prog.order_decision # since 2.0
    ctx = PolicyContext() # since 2.0
    team_prog.initialize(sku_info, frozen_history, xx.current_ip, ctx) # since 2.0

    for i in range(days): 
        demand = whole_demand_history[today]
        assert demand >= 0

        order_qty = policy(sku_info, frozen_history, xx.current_ip, ctx)
        assert order_qty >= 0

        xx.run_a_day(order_qty, demand)
        
        today += 1
        demand_history.append(demand)
        
    return xx.list_costs()

class frozenlist:
    '''a list that is incapable of modifying its own data'''
    __slots__ = ('__items',)

    def __init__(self, items):
        self.__items = items

    def __getitem__(self, index):
        return self.__items[index]

    def __len__(self):
        return self.__items.__len__()

    def __iter__(self):
        return self.__items.__iter__()

    def __eq__(self, other):
        return self.__items == other

    def __le__(self, other):
        return self.__items <= other

    def __repr__(self):
        return '({!r})'.format(self.__items)


# comma separated values
#import csv
import random
import sys

def read_SKUs(DATA = "SKU_DATA.csv"):
    with open(DATA, newline='') as csv_in:
        # skip the hearder line
        next(csv_in, None)
        
        rows = [line.split(',') for line in csv_in]
        # NO.,SKU,Unit Cost,Gross Profit,Lead Time,Cost/Order
            #print(','.join(row))
        return [SKU_Info(row[1], float(row[2]), float(row[3]),
                     int(row[4]), float(row[5]))
                for row in rows]         

def read_demands(DATA = "DEMAND_DATA.csv"):
    with open(DATA, newline='') as csv_in:
        next(csv_in, None) #skip the header line
        rows = [line.split(',') for line in csv_in]
        # NO.,SKU,d0,d1, ...
        return {row[1]:tuple(
            int(row[d]) for d in range(2, len(row)))
                for row in rows}         

import statistics as stats

def prepareSKU(sku_info, history, take_out_zeros):
    if take_out_zeros:
        for idx in range(len(history)):
            if history[idx]>0: break
        for idn in range(len(history)-1, idx-1, -1):
            if history[idn]>0: break
        history = history[idx: idn+1]

    mean = stats.mean(history)
    stdev = stats.stdev(history, mean)
    #log_info(f'mean: {mean:.2f}, stdev: {stdev:.2f}')

    return history, mean, stdev

####################################################
#
# The testing script starts here
#
####################################################

import importlib
# Team's implementation
TEAM_PROG =  "p1team"

if len(sys.argv) > 1:
    # may provide a different program file
    TEAM_PROG = sys.argv[1]
    if TEAM_PROG.lower().endswith('.py'):
        TEAM_PROG = TEAM_PROG[:-3]

import p1team

SKUs = read_SKUs()
demands = read_demands()

def test_phase_1(sku_info, history):
    history, mean, stdev = prepareSKU(sku_info, history, True)
    policy = p1team.reorder_upto
    return phase1test(sku_info, mean, stdev, policy, random, 30) #or 1000 days

def test_phase_2(sku_info, history):
    history, mean, stdev = prepareSKU(sku_info, history, False)
    initial_ip = int((mean+ stdev) * sku_info.lead_time_days)
    return phase2test(sku_info, initial_ip, history, p1team, 400)

# which phase of the project to test
tester = test_phase_1 # test_phase_1

summation = {'total':0, 'ordering':0, 'stockout':0, 'holding':0}

for sku_info in SKUs:
    history = demands[sku_info.SKU]
    costs = tester(sku_info, history)
    summation['total']+=costs[0]
    summation['ordering']+=costs[1]
    summation['holding']+=costs[2]
    summation['stockout']+=costs[3]
    print(f'{sku_info.SKU}: ordering={costs[1]:.2f}, holding={costs[2]:.2f}, stockout={costs[3]:.2f}, total={costs[0]:.2f}')
print('There are ',len(SKUs) ,'SKUs')
print(summation)
