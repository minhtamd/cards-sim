import yaml
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


CONFIG_PATH = "C:\\Users\\mtdoa\\OneDrive\\Documents\\Coding\\card simulation\\config.yaml"
LOS_LIST = ['shandi', 'azena', 'nineveh', 'balthorr', 'thirain', 'wei', 'kadan']

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def can_complete_los_30(total, mini, kadan_awakened, selectors):
    if kadan_awakened:
        return total + selectors - mini >= 80
    return total + selectors >= 96

def find_omitted(mini, cards, kadan_awakened):
    if not kadan_awakened:
        return 6
    for i in range(6):
        if mini == cards[i]:
            return i

""" Returns counts selectors X 2 array [[1 1]...selectors]"""
def run_trial_kadan(total, mini, freqs, cards, selectors):
    count = 0
    kadan_awakened = cards[6] >= 16

    counts = np.zeros((selectors + 1, 2), np.int32)
    # selectors x 2 array, where [count, card], count = # of legendary cards, card = which legendary card is omitted
    # [[4  3]
    #  [9  3]
    #  [15 5]]


    while selectors >= 0:
        if can_complete_los_30(total, mini, kadan_awakened, selectors):
            counts[selectors][0] = count
            # print(mini, cards, kadan_awakened, find_omitted(mini, cards, kadan_awakened))
            counts[selectors][1] = find_omitted(mini, cards, kadan_awakened)
            selectors -= 1
            continue

        count += 1

        # roll legend-rare mari card pack
        roll = random.randint(0, 100)
        if roll > 3:
            continue

        # roll legend card pack
        roll = random.randint(0, 19)
        if roll > 6: # not LoS, skip
            continue

        if cards[roll] >= 16: #skip if card is fully awakened
            continue

        if roll < 6: # roll non-kadan : 
            total += 1
            freqs[cards[roll]] -= 1 # decrease freq of old card's freq
            if cards[roll] == mini and freqs[cards[roll]] == 0: # change the minimum if needed
                mini += 1
            cards[roll] += 1 # increase card count
            freqs[cards[roll]] += 1 # increase freq of new card's freq
            # print(mini, cards, freqs[7:])

        elif roll == 6:
            cards[roll] += 1 # increase card count
            if cards[roll] == 16: # roll kadan and fully awakened
                kadan_awakened = True

    return counts

"""Returns data, a trials X selectors X 2 array [[[1 1]...selectors]...trials]"""
def run_simulation_kadan(trials, cards):
    total = 0
    mini = 16
    frequencies = [0]*17
    for c in cards[:-1]:
        c = min(16, c)
        mini = min(mini, c)
        frequencies[c] += 1    
        total += c
    
    data = np.zeros((trials, 96-total, 2), np.int32)
    for i in range(trials):
        data[i] = run_trial_kadan(total, mini, frequencies.copy(), cards.copy(), 95-total) # {95-total} is max number of selectors while not finishing los 30

    return data


def run_kadan(trials, cards, selectors):
    data = run_simulation_kadan(trials, cards)
    show_current_selectors(data, selectors)
    calc_selector_value(data, selectors)

def show_current_selectors(data, selectors):
    data = data[:,selectors,:]
    avg = np.average(data[:,0], axis=0)
    data_min = np.min(data)
    data_max = np.max(data)
    
    print('mari card packs:', avg)
    calc_cost(avg)

    datas = [[] for i in range(7)]
    for d in data:
        datas[d[1]].append(d[0])

    print()
    for i in range(7):
        print(f'chance to skip {LOS_LIST[i]}: {100*len(datas[i])/len(data)}%')

    plt.hist([np.array(datas[i]) for i in range(7)][::-1], np.arange(data_min, data_max, 50), stacked=True , label=LOS_LIST[::-1])
    plt.legend(prop={'size': 10})
    plt.show()

def calc_selector_value(data, selectors):
    difference_data = np.average(data[:,:-1,0]-data[:,1:,0], axis=0)

    s = config['selectors']

    print()
    for i in range(s, s+5):
        value = difference_data[i]
        print(f"At {i} selectors, they are worth {value} mari card packs ({int(round(value*calc_cost_per_card(), 0))} gold)")

    plt.plot(difference_data)
    plt.show()

def calc_cost_per_card():
    costs = config['card_cost']
    crystal_cost = costs['card_cost']/costs['card_amount']
    gold_per_crystal = costs['crystal_cost']/95
    gold_cost = gold_per_crystal*crystal_cost
    return gold_cost

def calc_cost(amount):
    costs = config['card_cost']
    card_pack_crystal_cost = costs['card_cost']/costs['card_amount']
    crystal_cost = amount*card_pack_crystal_cost
    gold_per_crystal = costs['crystal_cost']/95
    gold_cost = gold_per_crystal*crystal_cost
    print('crystals:', crystal_cost)
    print('gold:', gold_cost)

config = read_yaml(CONFIG_PATH)

trials = config['trials']
track_selectors = config['track_selectors']
selectors = config['selectors']
cards = list(config['salvation'].values())

run_kadan(trials, cards, selectors)
