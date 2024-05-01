
def welcome_message(name: str):
    return f"""
Welcome to $Sparkz Bot {name} 🎉🎉🎉
"""

def address_verified(address: str):
    return f"""
🔗✅ Successfully Linked SOL Wallet:

Use '/referral' to get referral link

<i>{address}</i>
"""

def airdrop_message():
    return """
Join our <a href="https://t.me/sparkzmarketplace_channel">official channel</a>

Join our <a href="https://t.me/sparkzmarketplace">Official Group</a>

Click on ✅ DONE to verify
"""

def air_drop_task(address: str):
    return f"""
Read carefully and perform these Twitter tasks to be able to complete airdrop.

⚠️ If you don't complete this task, you won't be able to claim your airdrop at TGE. To avoid disqualification, you have to complete this task ⚠️

🐦 Follow our Twitter Page <a href="https://x.com/SparkzStore?t=v0qDofejco5SuRpoxG9BeQ&s=09">@sparkzstore</a> click the 🔔 icon and turn on notifications for our posts on X.

♻️ Like and Retweet the pinned tweet, copy the solana wallet 👛 below and submit it to the pinned tweet as a reply.

<i>{address}</i>

✍️When done, press the ✅ Verify Airdrop Data button to proceed.
"""

def share_twitter_link():
    return """
✍️ After posting the reply, tap on share, copy the link to your comment and send here for verification. (share link in message box below 👇)
"""

def not_done_twitter_task():
    return """
⚠️All missions and links submitted will be verified before airdrop claim.
 
If completed, click  ✅️DONE
"""

def sparkz_balance(**kwargs):
    return f"""
Here is your $SPARKZ Token Balance.

💰 Airdrop Balance: {kwargs["token_balance"]}
💰 Presale Balance: {kwargs["presale_balance"]} $SPARKZ
💰 Mission Balance: {kwargs["mission_balance"]} 

🔗 Linked Wallet : 

<i>{kwargs["address"]}</i>

"""