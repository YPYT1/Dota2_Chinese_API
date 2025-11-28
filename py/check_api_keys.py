"""
验证硅基流动 API Keys 是否可用
"""
import json
import urllib.request
import urllib.error
import concurrent.futures
import time

# 所有 API Keys
API_KEYS = [
    "sk-siewfnhirxiblasfmuhenyreyhhwikebduvlksfvxwkfuxdy",
    "sk-msjpxhijsiboucxqjxqjxxjliqblosqcjpifavjhspdahgsi",
    "sk-nhzgadejdkyopwwxkqoacykslssbpkgxnynsvowrvazvitxj",
    "sk-jbhgionjcahjufqppjgorpspsahxmjycvyytiztrgwyynsen",
    "sk-zooquxwgjluqwuqitcahtibpjvometznizxesrbsyratfdit",
    "sk-nmflxcgetbblqfamxwfgmcunkflqcbpcrzsumeuqpxtncygs",
    "sk-dmzoetsqcvvavmcafyncaovlhefziwrmazeymgkkrppaxufi",
    "sk-vjznbbzzwcndnrqetmymoayuwwaxlpbhvdjlqoezfsbpjsiq",
    "sk-pagzocjzmwjfuhsjwvjmlsiirmhepngwcvgngmyxtreyouan",
    "sk-klvunpibdsowqwtolcsrkuxzchfhauekqiyqregwlpynejdl",
    "sk-ypxteqomusjspwhjdhosvklyqtsujjntptzxlekkzkgifinw",
    "sk-gdqxfsdaaxhfczjhoidbmhmcoyaghpghuavmgealfdtlzrlx",
    "sk-bthvofnulooittgysgocmhoohfxprouzjtkghwnaylegkxrz",
    "sk-nmzahpgdyrvzaspfziuubamguvijbebvkgowijldfiuoakso",
    "sk-sxilebnzfwwpseccpoexasbmhdyuwljmnpaiiregezolxvtl",
    "sk-ueiisviuxnzzqjqjlicbiezokdhffldmayjwhlcskjipgxcq",
    "sk-bawwaelrizmhtfffpnhvwakjitsaukhxugazqosqwnewvkvd",
    "sk-wkccpljuyztixirudpmsuafbhlrkzofjkwlkpsappsqdddgg",
    "sk-sfdvgdbccapzkfnnzrtvcqjnjawhnxhftoqswbovnfrbngai",
    "sk-dgwbhtkscbbaewogaagdoxdzremrwhytlfgvdvzrvhtnytde",
    "sk-vkvulhudkumfpbomsbjoawfwbyautrzuhrxiaoznljddaxpz",
    "sk-zbcyicmeevbldbmzhqbvcawixljyisomsryvxbklzbikepiy",
    "sk-vlufavsapaxluzyvtgospverzympftzlmjbkrcvdyaojrrta",
    "sk-lzsponisjomzgwwntfxllglnkoudekocjxfpqheihqewkqpr",
    "sk-itwasjvgbsmqtnbrkzlyjihlypxovpfdkfqkolsxqcceuwhh",
    "sk-treaxnishzqqhcmrmybersfgfubwhxukxmupiwyxdtlqhnlr",
    "sk-dpvfkfnkoqmrufbelqatxcyhftlciddacsfcjnetpkxcuwfy",
    "sk-jomxxxgqhydiwwqpfvwjoipfhgtfgybfrvgbmngjmjsqaroe",
    "sk-xqsgeepwhjkfogvlrytwvjcxcbhvnzfzmnlisukblxlgyypd",
    "sk-exhpneambxyuppmtjjgtvftzybcuibrfnzmdcfcznkdwxakj",
    "sk-emgppuptgfhmrrysnkgffjftslclepsiauyudnwmcbxlsboz",
    "sk-hiyunrilosxlongugnflecekkmgdbfpclkzuqamvayboajur",
    "sk-tiqmxmdrorfalhimtvyciwczpaunsntomwrkyodytdaphytb",
    "sk-isbrudoqglivvyxvadgripshmgilykwyjbbyykxrqqbleofu",
    "sk-llawuafmqmjkbupvkyfcmhulqendjhcmkrctqixvfnmxjebl",
    "sk-taxusxjaajchjtakvpaxrljegfazixobegjkexoibzopqzhc",
    "sk-fnfefpeoqqiqiqwsaumohogerzojbszebdcseofpcnlrzofd",
    "sk-cbaletqlvdlpuavqudxyoyuyntrhauzwsjfluxapkuawgtwl",
    "sk-etradeaoutcspltqiwrayyejncsrtqdtlzypawgyjvlaktpp",
    "sk-nqxhcujfekvovgiqtpcsymzucegakbpivplnkrhdurezcfgg",
    "sk-ozhmwqgcgzahosuqbbvtybgmydctzhcaqqgxlyahrznupweo",
    "sk-uvruvnttmumjenbcrayghxjpzasejxtupdzqrgmfjwxhbqgp",
    "sk-hbetfvohxcpqtarvgcemoucusiwepimwjeqkehhesrdqrvfk",
    "sk-rgzwjxagiichrcmemnydayzzjfuflgxitlzgvibnvptrpgmr",
    "sk-yzxrhjczekerrultdoszzozkyeqfeucdwlnlcebyadkweunc",
    "sk-twauyuvupwohoxjtzlthboprbglwtbhuyovfhuhgtgzgqbhw",
    "sk-fknagdkobdmqynreyoiwiaojqmkunixanmcvknvujkfxkpeq",
    "sk-swyvfuczlfyjhgsbpxvcllkalxgoxdcxrwqajhzfzttyjkcf",
    "sk-lppjzqqgwavkqbppxnhedkrujtuuavpresmecspbmjbeenkx",
    "sk-sdckehthwoxdhqxuctnaushkfdroqcjrkcjxbrsxchkrqryo",
    "sk-zzprirejmieynxesllnzpvmugohsowwfgxaxgsfkclhqfcin",
    "sk-umshijegkxfllmmekwppjlnidwjznblvgschkanzcraxkbqj",
    "sk-mvliscganbuniicouxodljrpojembdprrpateslgeqebxgzb",
    "sk-wvlmkxvffbrmlujaohsjilymyqkawlvninajinrptndawyfj",
    "sk-jjdttvtyjhroxqyaazprdqwyyjkspdaxcdivekatbpigcorc",
    "sk-rnttbjkyqecmfvawiudeshzboffzgkacblyccejpqaadxfqa",
    "sk-ftrvjhpxuowevsazmtkeyjgnnwvcwdekapivdecdngrozrru",
    "sk-giyrsswaqyeicyyoqvjjbrhxaehijeiqswvelsmgkyjxzhri",
    "sk-utpfvxpysmpgruircdmgtkvqfctkrxvvqpbkrszhyqmmjbrg",
    "sk-mtnudcrllturtgldzimycmwwytcbszxdhfkwxqsrfpwkrhua",
    "sk-ckjtfrgokysykcxirrweatsvmimpvpzlrpchwjkvnlefihhw",
    "sk-dlnrxtgfhsznczsyfiztxcafybhhhahaygdscvsbadrbclhq",
    "sk-gyavazkayfscmsxjyxenpndtzcvcegvzkfojlpqdzoerrvxn",
    "sk-rjviuovnerljdfxyojpsuacmbbjeqgiktfdjjwqycddzdmss",
    "sk-acomjgudhnaogipyjotuyqsejxmzhpqrbyzzxewqudrzqqdm",
    "sk-igvsaeiwwxetgbmfcjfexustykgdwztqolkamqtrxpzohoyv",
    "sk-hbsauorsqvsswprdoimpshlnsxrliuxwvalzgulxfyfbqjgh",
    "sk-ryemtlzbzsofgooiplqnlgztmpzkqxwlvlgbrpvcrttogvrw",
    "sk-rgrkqkflpicvlffyvalaprzqhggwoqodztnswhxrwemjvqxa",
    "sk-pghzivovobvnkqddzkjclddvgrukqaregrqbbaxbanudsssa",
    "sk-jhwhtpyfmouosfugyeadghzutdxldwuwcpirizayqztbtxcq",
    "sk-lnlnfegwfecphfrgkeoyhkbyoztrgdfzpdurrnstixobnvyj",
    "sk-crlgwnsmsssnguwryspchslwilwijchmrglehwgskupycjvv",
    "sk-cqiqirzzcjmcktyohrleaenvpzacevqyvcfcauyftfduxwjo",
    "sk-dfixatbrylnyhbfzcqnixarblqoxnrxdzbldfkhskpwyuxah",
    "sk-dxlmmqsrmuzotjsucwglczeclxdplguamdysxxtsphftxcqu",
    "sk-uhkniuptnnivtdcjlbwytycsokydakyqhxwiemkyewvnvzdz",
    "sk-yerytckfknvedlsaxmdeupaaixmqfgbdnesqvmfccokbjkgx",
    "sk-pkskbfidrshqdgeunzbrfbqgsttedryjlhibpdcfnordmgqm",
    "sk-ayksyrkdakkiqsufvtmmvjugtlqbobrnziurfxainmomvgxl",
    "sk-xoghbzikpqofuiidhvatwmqgywsomfjqzcxpqlmmxsoubkbb",
    "sk-cxdemrjygyguqbuqralqeedfirdxvgwekaoylotrcrnwpsbn",
    "sk-ihxyyyipuuapiercbfyjuqrtpxysgqmnkjretuawnzzijmnj",
    "sk-xhepadshahakjlcdqdoiqvheqjuqvsbpfkkjzlwfokbpqpce",
    "sk-xkrxtkwtfzangggbrnjmwxwokaoglmkwyeohzdndnjfnomzv",
    "sk-ezicqmnfmsfbcoubiunszpxytfsoohgoogvbidohpdwmurij",
    "sk-bxhuzomgogacallgsxvnyibgbkxhosrwhipzpzglxqjgrcys",
    "sk-qqnduqlvxvunivepxfzoqrwpcsxbpcnfkrbxvjzzaxnqgqek",
    "sk-jblojllmqlppylacjzydvrqhzjkuzxgxvnolhtxpagosvoae",
    "sk-ehdobrekhzesxlenfgwiwkgvhnovysfryuyizfdrghffgkwb",
    "sk-fnhqysisvjhckcgdtveqscehwltpdevthpwtkveursiijaok",
    "sk-uwjmnklilvmcykgjupzxukksdztxjgdgebijzaicfsaljjwd",
    "sk-axbscnqeeonozbewfwnaruboafktwdbnyqodhmcglanninjb",
    "sk-ldfbzxayfphkkewkghusprvnkyrbinwzwubtwircuiohivez",
    "sk-ytuccnkstkfktitcqcvwtspdmkxrjgffdcklwenhqhoakveh",
    "sk-lvqqleupizdzsnvziymitzcodznfvzqsqrlkujxydcslkdeb",
    "sk-uiyvtahyduzgvvrrtuiznlrolvtcvaifnrsvspcbtzciukgw",
    "sk-ixwmenavwkhppjkwsslhgidvlibtpirwfcvrchazskvxlcic",
    "sk-ytybxacuennonrqivvbpztqafrcrfginiqggoxshonfwwcry",
    "sk-gzzenguczvfnecaaklptddgtibntyrepeaczrhwumampjwde",
]

BASE_URL = "https://api.siliconflow.cn/v1"


def check_single_key(args):
    """检查单个 API Key"""
    index, api_key = args
    
    req = urllib.request.Request(
        f"{BASE_URL}/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return {"index": index, "key": api_key[:20] + "...", "status": "✅ 有效", "code": resp.status}
    except urllib.error.HTTPError as e:
        return {"index": index, "key": api_key[:20] + "...", "status": "❌ 无效", "code": e.code}
    except urllib.error.URLError as e:
        return {"index": index, "key": api_key[:20] + "...", "status": "⏱️ 超时/网络错误", "code": 0}
    except Exception as e:
        return {"index": index, "key": api_key[:20] + "...", "status": "❌ 错误", "code": 0, "error": str(e)[:50]}
    
    return {"index": index, "key": api_key[:20] + "...", "status": "❌ 未知", "code": 0}


def main():
    """主函数：多线程检查所有 API Keys"""
    print(f"开始检查 {len(API_KEYS)} 个 API Keys...\n")
    
    valid_keys = []
    invalid_keys = []
    
    # 多线程并发检查
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        args_list = [(i, key) for i, key in enumerate(API_KEYS)]
        results = list(executor.map(check_single_key, args_list))
    
    for result in results:
        status_icon = result['status']
        print(f"[{result['index']+1:3d}] {result['key']} {status_icon}")
        
        if "有效" in result['status']:
            valid_keys.append(API_KEYS[result['index']])
        else:
            invalid_keys.append(API_KEYS[result['index']])
    
    # 统计
    print("\n" + "=" * 60)
    print(f"检查完成！")
    print(f"  有效: {len(valid_keys)} 个")
    print(f"  无效: {len(invalid_keys)} 个")
    print("=" * 60)
    
    # 保存有效的 keys
    if valid_keys:
        with open("valid_api_keys.json", "w") as f:
            json.dump({"keys": valid_keys, "count": len(valid_keys)}, f, indent=2)
        print(f"\n有效的 API Keys 已保存到: valid_api_keys.json")


if __name__ == "__main__":
    main()
