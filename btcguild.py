#!/usr/bin/python
import json
import subprocess
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('btcguild.conf')

#Config Options
API_KEY = config.get('btcguild', 'API_KEY')
CURL_PATH = config.get('btcguild', 'CURL_PATH')

my_stats = subprocess.check_output([CURL_PATH, '-s', 'http://www.btcguild.com/api.php?api_key=' + API_KEY])
block_stats = subprocess.check_output([CURL_PATH, '-s', 'http://www.btcguild.com/recent_blocks.php'])

my_json = json.loads(my_stats)
block_json = json.loads(block_stats)

#Calculate personal stats
conf = my_json['user']['confirmed_rewards']
unconf = my_json['user']['unconfirmed_rewards']
est = my_json['user']['estimated_rewards']

hashrate = shares = stales = i = 0
for worker in my_json['workers']:
	hashrate += my_json['workers'][worker]['hash_rate']
	shares += my_json['workers'][worker]['round_shares']
	stales += my_json['workers'][worker]['round_stales']

if(shares > 0 and stales > 0) :
	stale_perc = float(stales)/float(shares) * 100
else:
	stale_perc = 0.0

#calculate recen block stats
def toSeconds(time) :
	time = time.split(':')
	seconds = int(time[0]) * 3600
	seconds += int(time[1]) * 60 
	seconds += int(time[2])
	return float(seconds)

total_blocks = total_seconds = total_un = 0
for block in block_json['blocks']:
	total_blocks += 1
	if(int(block['validity']) < 120) :
		total_un += 1
	total_seconds += toSeconds(block['duration'])
avg_speed = total_seconds/total_blocks
avg_blocks = 24 * 60 * 60 / avg_speed
est_pb = unconf/total_un
if(unconf == 0 or total_un >= 25) :
	est_pb = est


print "+-+-+-+-BTC GUILD Pool Stats for %s-+-+-+-+" % API_KEY
print "+ Confirmed Payout   : %.8f                                       +" % conf
print "+ Unconfirmed Payout : %.8f                                       +" % unconf
print "+ Estimated Payout   : %.8f                                       +" % est
print "+ Sum Total (inc est): %.8f                                       +" % round(conf+unconf+est,8)
print "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
for worker in my_json['workers']:
	workerhashrate = my_json['workers'][worker]['hash_rate']
	workershares = my_json['workers'][worker]['round_shares']
	workerstales = my_json['workers'][worker]['round_stales']
	if(workershares > 0 and workerstales > 0) :
		workerstale_perc = float(workerstales)/float(workershares) * 100
	else:
		workerstale_perc = 0.0
	print "+ Worker name: %s     					+" % (my_json['workers'][worker]['worker_name'])
	print "+ Worker Hashrate %.2f  Shares %d  Stales %d  Stale%% %.2f             +" % (workerhashrate,  workershares, workerstales, workerstale_perc)
	print "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
print "+ Total Worker Hashrate %.2f  Shares %d  Stales %d  Stale%% %.2f       +" % (hashrate,  shares, stales, stale_perc)
print "+ Pool Average Block Time (seconds) %.0f   Round Time %s           +" % (avg_speed, my_json['pool']['round_time'])
print "+ Latest Block Times   %s %s %s %s %s %s  +" % ( block_json['blocks'][0]['duration'], block_json['blocks'][1]['duration'], block_json['blocks'][2]['duration'], block_json['blocks'][3]['duration'], block_json['blocks'][4]['duration'], block_json['blocks'][5]['duration'])
print "+ Pool Est Blks/24hrs   %.0f      Miner Est 24hr Rewards : %.8f     +" % (avg_blocks, avg_blocks * est_pb)
print "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
