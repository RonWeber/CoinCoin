# -*- coding: utf-8 -*-
#Coincoin: Cryptocurrency maker
#Dependencies: A lot.  Like, it would be easier to list the things this doesn't depend on.

import shutil, os, multiprocessing, subprocess, wx, threading
from srcFromElsewhere.GenesisH0 import genesis

#TODO: Bigger premine ($)

REWARD_PUBKEY="04891F6A627BFC5D16FCF4FDFB6D4A63E8E0C818274064D026FA9A99603EA16542F55B85006F0F3545EE1024905AB58E4467CCE731325AD4EB098E6163FCDBD879"

LITECOIN_PUB_KEY="040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9"
LITECOIN_MERKLE_HASH="97ddfbbae6be97fd6cdf3e7ca13232a3afff2353e29badfab7f73011edd4ced9"
LITECOIN_MAIN_GENESIS_HASH="12a765e31ffd4059bada1e25190f6e98c99d9714d334efa41a195a7e7e04bfe2"
LITECOIN_TEST_GENESIS_HASH="4966625a4b2851d9fdee139e56211a0d88575f59ed816ff5e6a63deb4e3e29a0"
LITECOIN_REGTEST_GENESIS_HASH="530827f38f93b43ed12af0b3ad25a288dc02ed74d6d7857862df51fc56c416f9"
MINIMUM_CHAIN_WORK_MAIN="0x000000000000000000000000000000000000000000000006805c7318ce2736c0"
MINIMUM_CHAIN_WORK_TEST="0x000000000000000000000000000000000000000000000000000000054cb9e7a0"


def renameFilesAndReplaceLitecoin(name, tla, main_port, test_port, phrase, pubkey_char, coinbase_maturity, reward_pubkey):
    for (path, dirnames, filenames) in os.walk("output/" + name.lower(), True):
        for directory in dirnames:
            #Do we need to rename this directory?
            if "litecoin" in directory:
                newName = directory.replace("litecoin", name.lower())
                shutil.move(os.path.join(path, directory), os.path.join(path, newName))
                dirnames.remove(directory)
                dirnames.append(newName)
        for filename in filenames:
            if "litecoin" in filename:
                newName = filename.replace("litecoin", name.lower())
                shutil.move(os.path.join(path, filename), os.path.join(path, newName))
                #Don't need to change the list.  It's not like it'll be used again.
            else:
                newName = filename
            #Now we change the contents.
            with open(os.path.join(path, newName)) as f:
                entireFile = f.read()
            try:
                entireFile = entireFile.replace("Litecoin", name)
                entireFile = entireFile.replace("litecoin", name.lower())
                entireFile = entireFile.replace("LITECOIN", name.upper())
                entireFile = entireFile.replace("LTC", tla)
            except UnicodeDecodeError: #We gotta ignore binary files.
                print "Ignoring file " + os.path.join(path, newName)
            with open(os.path.join(path, newName), 'w') as f:
                f.write(entireFile)

def setChainParams(chainParamsFilename, genesis_parameters, test_genesis_parameters, main_port, test_port, phrase, pubkey_char, coinbase_maturity, reward_pubkey ):
    with open(chainParamsFilename) as f:
        chainParams = f.read()
    chainParams = chainParams.decode("utf-8")
    chainParams = chainParams.replace("1,48", "1," + pubkey_char)
    chainParams = chainParams.replace("1317972665", genesis_parameters["time"])
    chainParams = chainParams.replace("1486949366", test_genesis_parameters["time"])
    chainParams = chainParams.replace(u"NY Times 05/Oct/2011 Steve Jobs, Apple’s Visionary, Dies at 56", phrase)
    chainParams = chainParams.replace("9333", main_port)
    chainParams = chainParams.replace("19335", test_port)
    #pubkey
    chainParams = chainParams.replace(LITECOIN_PUB_KEY, REWARD_PUBKEY)
    #Merkle hash
    chainParams = chainParams.replace(LITECOIN_MERKLE_HASH, genesis_parameters["merkle_hash"])
    chainParams = chainParams.replace(LITECOIN_MAIN_GENESIS_HASH, genesis_parameters["genesisHash"])
    chainParams = chainParams.replace(LITECOIN_TEST_GENESIS_HASH, test_genesis_parameters["genesisHash"])
    chainParams = chainParams.replace(LITECOIN_REGTEST_GENESIS_HASH, test_genesis_parameters["genesisHash"])
    chainParams = chainParams.replace("2084524493", genesis_parameters["nonce"])
    chainParams = chainParams.replace("293345", test_genesis_parameters["nonce"])
    chainParams = chainParams.replace("0x1e0ffff0", genesis_parameters["bits"])
    chainParams = chainParams.replace("COINBASE_MATURITY = 100", "COINBASE_MATURITY = " + coinbase_maturity)
    chainParams = chainParams.replace(MINIMUM_CHAIN_WORK_MAIN, "0x00")
    chainParams = chainParams.replace(MINIMUM_CHAIN_WORK_TEST, "0x00")
    #bip activation heights
    chainParams = chainParams.replace("710000", "0") 
    chainParams = chainParams.replace("918684", "0")
    chainParams = chainParams.replace("811879", "0")
    chainParams = chainParams.encode("utf-8")
    with open(chainParamsFilename, "w") as f:
        f.write(chainParams)

def build(name):
    working_directory = "output/" + name.lower()
    subprocess.call(["./autogen.sh"], shell=True, cwd=working_directory)
    subprocess.call(["./configure"], shell=True, cwd=working_directory)
    make_jobs = multiprocessing.cpu_count() + 1
    subprocess.call(["make", "-j" + str(make_jobs)], shell=True, cwd=working_directory)

class Frame(wx.Frame):
    def __init__(self, title):
        self.textFields = {}
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(700,700))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        
        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        
        coinCoinLabel = wx.StaticText(panel, -1, "CoinCoin")
        coinCoinLabel.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
        coinCoinLabel.SetSize(coinCoinLabel.GetBestSize())
        box.Add(coinCoinLabel, 0, wx.ALL | wx.CENTER, 10)

        sloganLabel = wx.StaticText(panel, -1, "Because the world needs more cryptocurrencies")
        sloganLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        sloganLabel.SetSize(sloganLabel.GetBestSize())
        box.Add(sloganLabel, 0, wx.ALL | wx.CENTER, 10)

        self.addControls(panel, box, "name", "Coin Name:", "CoinCoinCoin")
        self.addControls(panel, box, "tla", "Three Letter Acronym:", "CCC")
        self.addControls(panel, box, "main_port", "Mainnet port:", "31415")
        self.addControls(panel, box, "test_port", "Testnet port:", "51413")
        self.addControls(panel, box, "phrase", "Timestamp Phrase:", "Clickhole 1/17/2018 Cryptocurrency Crash: The Value Of Bitcoin Has Cratered After Investors Pulled All Of Their Money Out And Put It Into Collecting State Quarters")
        self.addControls(panel, box, "pubkey_char", "First letter of wallet address (in base 58)", "24")
        self.addControls(panel, box, "coinbase_maturity", "Coinbase maturity:", "100")
        self.addControls(panel, box, "reward_pubkey", "Reward Public Key", "04891F6A627BFC5D16FCF4FDFB6D4A63E8E0C818274064D026FA9A99603EA16542F55B85006F0F3545EE1024905AB58E4467CCE731325AD4EB098E6163FCDBD879")

        goButton = wx.Button(panel, -1, "MAKE CRYPTOCURRENCY")
        goButton.Bind(wx.EVT_BUTTON, self.goButtonClicked)
        box.Add(goButton, 0, wx.ALL | wx.EXPAND, 10)

        buildButton = wx.Button(panel, -1, "Build")
        buildButton.Bind(wx.EVT_BUTTON, self.buildButtonClicked)
        box.Add(buildButton, 0, wx.ALL | wx.EXPAND, 10)

        m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        box.Add(m_close, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(box)
        panel.Layout()

    def addControls(self, panel, box, control_name, control_label, default_value):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(panel, -1, control_label)
        text = wx.TextCtrl(panel, -1, default_value)
        self.textFields[control_name] = text
        sizer.Add(lbl, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(text, 1, wx.ALL | wx.EXPAND, 5)
        box.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

    def goButtonClicked(self, event):
        event.GetEventObject().Disable() #Making the same cryptocurrency twice in parallel can only go well!
        thread = threading.Thread(target=makeCurrency,
                                  args=(self.textFields["name"].GetValue(),
                                        self.textFields["tla"].GetValue(),
                                        self.textFields["main_port"].GetValue(),
                                        self.textFields["test_port"].GetValue(),
                                        self.textFields["phrase"].GetValue(),
                                        self.textFields["pubkey_char"].GetValue(),
                                        self.textFields["coinbase_maturity"].GetValue(),
                                        self.textFields["reward_pubkey"].GetValue(),))
        thread.start()

    def buildButtonClicked(self, event):
        thread = threading.Thread(target=build,
                                  args=(self.textFields["name"].GetValue(),))
        thread.start()

                                        
                                        

    def OnClose(self, event ):
        self.Destroy()


def makeCurrency(name, tla, main_port, test_port, phrase, pubkey_char, coinbase_maturity, reward_pubkey):
    print name
    print tla
    print main_port
    print test_port
    print "Let's make a Genesis block!"
    #genesis_parameters  = genesis.main(phrase, reward_pubkey)
    genesis_parameters = {'nonce': '852641', 'pszTimestamp': u'Clickhole 1/17/2018 Cryptocurrency Crash: The Value Of Bitcoin Has Cratered After Investors Pulled All Of Their Money Out And Put It Into Collecting State Quarters', 'algorithm': 'scrypt', 'time': '1518950770', 'bits': '0x1e0ffff0', 'pubkey': u'04891F6A627BFC5D16FCF4FDFB6D4A63E8E0C818274064D026FA9A99603EA16542F55B85006F0F3545EE1024905AB58E4467CCE731325AD4EB098E6163FCDBD879', 'genesisHash': '607ab61689cafa5be357f7098ca0223812a1e2de089303b82179e83a8a36eabb', 'merkle_hash': 'aaf90043a6183aa5d52a4b066c41cc83086ab699d012a5e19daaec2303e8fced'}

    
    print "FOUND IT!"
    print genesis_parameters

    print "We have to make a test genesis block, too? :("
    #Potential bug: If we somehow get the genesis hash in <1 second, the test block will be identical.
    #test_genesis_parameters = genesis.main(phrase, reward_pubkey)
    test_genesis_parameters = {'nonce': '852641', 'pszTimestamp': u'Clickhole 1/17/2018 Cryptocurrency Crash: The Value Of Bitcoin Has Cratered After Investors Pulled All Of Their Money Out And Put It Into Collecting State Quarters', 'algorithm': 'scrypt', 'time': '1518950770', 'bits': '0x1e0ffff0', 'pubkey': u'04891F6A627BFC5D16FCF4FDFB6D4A63E8E0C818274064D026FA9A99603EA16542F55B85006F0F3545EE1024905AB58E4467CCE731325AD4EB098E6163FCDBD879', 'genesisHash': '607ab61689cafa5be357f7098ca0223812a1e2de089303b82179e83a8a36eabb', 'merkle_hash': 'aaf90043a6183aa5d52a4b066c41cc83086ab699d012a5e19daaec2303e8fced'}

    
    print "FOUND IT!"
    print test_genesis_parameters

    print "Copying stuff..."
    shutil.copytree("srcFromElsewhere/litecoin", "output/" + name.lower(), True)
    print "Renaming files..."
    renameFilesAndReplaceLitecoin(name, tla, main_port, test_port, phrase, pubkey_char, coinbase_maturity, reward_pubkey)
    print "Setting parameters..."
    setChainParams(os.path.join("output", name.lower(), "src", "chainparams.cpp"), genesis_parameters, test_genesis_parameters, main_port, test_port, phrase, pubkey_char, coinbase_maturity, reward_pubkey)

    print name + " is ready!"
    #print "We're going to go ahead and build it for you, too."
    #build()
    #print "Built complete!"

def main():
    app = wx.App()
    top = Frame("Hello World")
    top.Show()
    app.MainLoop()
    
    

main()
