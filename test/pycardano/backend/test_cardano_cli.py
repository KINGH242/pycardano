import json
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from pycardano import (
    ALONZO_COINS_PER_UTXO_WORD,
    CardanoCliChainContext,
    CardanoCliError,
    CardanoCliNetwork,
    DatumHash,
    GenesisParameters,
    MultiAsset,
    PlutusV2Script,
    ProtocolParameters,
    PyCardanoException,
    RawPlutusData,
    TransactionFailedException,
    TransactionInput,
)
from pycardano.backend.cardano_cli import network_magic

QUERY_TIP_RESULT = {
    "block": 1460093,
    "epoch": 98,
    "era": "Babbage",
    "hash": "c1bda7b2975dd3bf9969a57d92528ba7d60383b6e1c4a37b68379c4f4330e790",
    "slot": 41008115,
    "slotInEpoch": 313715,
    "slotsToEpochEnd": 118285,
    "syncProgress": "100.00",
}

QUERY_PROTOCOL_PARAMETERS_RESULT = {
    "collateralPercentage": 150,
    "costModels": {
        "PlutusV1": [
            205665,
            812,
            1,
            1,
            1000,
            571,
            0,
            1,
            1000,
            24177,
            4,
            1,
            1000,
            32,
            117366,
            10475,
            4,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            100,
            100,
            23000,
            100,
            19537,
            32,
            175354,
            32,
            46417,
            4,
            221973,
            511,
            0,
            1,
            89141,
            32,
            497525,
            14068,
            4,
            2,
            196500,
            453240,
            220,
            0,
            1,
            1,
            1000,
            28662,
            4,
            2,
            245000,
            216773,
            62,
            1,
            1060367,
            12586,
            1,
            208512,
            421,
            1,
            187000,
            1000,
            52998,
            1,
            80436,
            32,
            43249,
            32,
            1000,
            32,
            80556,
            1,
            57667,
            4,
            1000,
            10,
            197145,
            156,
            1,
            197145,
            156,
            1,
            204924,
            473,
            1,
            208896,
            511,
            1,
            52467,
            32,
            64832,
            32,
            65493,
            32,
            22558,
            32,
            16563,
            32,
            76511,
            32,
            196500,
            453240,
            220,
            0,
            1,
            1,
            69522,
            11687,
            0,
            1,
            60091,
            32,
            196500,
            453240,
            220,
            0,
            1,
            1,
            196500,
            453240,
            220,
            0,
            1,
            1,
            806990,
            30482,
            4,
            1927926,
            82523,
            4,
            265318,
            0,
            4,
            0,
            85931,
            32,
            205665,
            812,
            1,
            1,
            41182,
            32,
            212342,
            32,
            31220,
            32,
            32696,
            32,
            43357,
            32,
            32247,
            32,
            38314,
            32,
            57996947,
            18975,
            10,
        ],
        "PlutusV2": [
            205665,
            812,
            1,
            1,
            1000,
            571,
            0,
            1,
            1000,
            24177,
            4,
            1,
            1000,
            32,
            117366,
            10475,
            4,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            23000,
            100,
            100,
            100,
            23000,
            100,
            19537,
            32,
            175354,
            32,
            46417,
            4,
            221973,
            511,
            0,
            1,
            89141,
            32,
            497525,
            14068,
            4,
            2,
            196500,
            453240,
            220,
            0,
            1,
            1,
            1000,
            28662,
            4,
            2,
            245000,
            216773,
            62,
            1,
            1060367,
            12586,
            1,
            208512,
            421,
            1,
            187000,
            1000,
            52998,
            1,
            80436,
            32,
            43249,
            32,
            1000,
            32,
            80556,
            1,
            57667,
            4,
            1000,
            10,
            197145,
            156,
            1,
            197145,
            156,
            1,
            204924,
            473,
            1,
            208896,
            511,
            1,
            52467,
            32,
            64832,
            32,
            65493,
            32,
            22558,
            32,
            16563,
            32,
            76511,
            32,
            196500,
            453240,
            220,
            0,
            1,
            1,
            69522,
            11687,
            0,
            1,
            60091,
            32,
            196500,
            453240,
            220,
            0,
            1,
            1,
            196500,
            453240,
            220,
            0,
            1,
            1,
            1159724,
            392670,
            0,
            2,
            806990,
            30482,
            4,
            1927926,
            82523,
            4,
            265318,
            0,
            4,
            0,
            85931,
            32,
            205665,
            812,
            1,
            1,
            41182,
            32,
            212342,
            32,
            31220,
            32,
            32696,
            32,
            43357,
            32,
            32247,
            32,
            38314,
            32,
            35892428,
            10,
            57996947,
            18975,
            10,
            38887044,
            32947,
            10,
        ],
    },
    "decentralization": None,
    "executionUnitPrices": {"priceMemory": 5.77e-2, "priceSteps": 7.21e-5},
    "extraPraosEntropy": None,
    "maxBlockBodySize": 90112,
    "maxBlockExecutionUnits": {"memory": 62000000, "steps": 20000000000},
    "maxBlockHeaderSize": 1100,
    "maxCollateralInputs": 3,
    "maxTxExecutionUnits": {"memory": 14000000, "steps": 10000000000},
    "maxTxSize": 16384,
    "maxValueSize": 5000,
    "minPoolCost": 340000000,
    "minUTxOValue": None,
    "monetaryExpansion": 3.0e-3,
    "poolPledgeInfluence": 0.3,
    "poolRetireMaxEpoch": 18,
    "protocolVersion": {"major": 8, "minor": 0},
    "stakeAddressDeposit": 2000000,
    "stakePoolDeposit": 500000000,
    "stakePoolTargetNum": 500,
    "treasuryCut": 0.2,
    "txFeeFixed": 155381,
    "txFeePerByte": 44,
    "utxoCostPerByte": 4310,
    "utxoCostPerWord": None,
}

QUERY_UTXO_RESULT = {
    "fbaa018740241abb935240051134914389c3f94647d8bd6c30cb32d3fdb799bf#0": {
        "address": "addr1x8nz307k3sr60gu0e47cmajssy4fmld7u493a4xztjrll0aj764lvrxdayh2ux30fl0ktuh27csgmpevdu89jlxppvrswgxsta",
        "datum": None,
        "inlineDatum": {
            "constructor": 0,
            "fields": [
                {
                    "constructor": 0,
                    "fields": [
                        {
                            "bytes": "2e11e7313e00ccd086cfc4f1c3ebed4962d31b481b6a153c23601c0f"
                        },
                        {"bytes": "636861726c69335f6164615f6e6674"},
                    ],
                },
                {"constructor": 0, "fields": [{"bytes": ""}, {"bytes": ""}]},
                {
                    "constructor": 0,
                    "fields": [
                        {
                            "bytes": "8e51398904a5d3fc129fbf4f1589701de23c7824d5c90fdb9490e15a"
                        },
                        {"bytes": "434841524c4933"},
                    ],
                },
                {
                    "constructor": 0,
                    "fields": [
                        {
                            "bytes": "d8d46a3e430fab5dc8c5a0a7fc82abbf4339a89034a8c804bb7e6012"
                        },
                        {"bytes": "636861726c69335f6164615f6c71"},
                    ],
                },
                {"int": 997},
                {
                    "list": [
                        {
                            "bytes": "4dd98a2ef34bc7ac3858bbcfdf94aaa116bb28ca7e01756140ba4d19"
                        }
                    ]
                },
                {"int": 10000000000},
            ],
        },
        "inlineDatumhash": "c56003cba9cfcf2f73cf6a5f4d6354d03c281bcd2bbd7a873d7475faa10a7123",
        "referenceScript": None,
        "value": {
            "2e11e7313e00ccd086cfc4f1c3ebed4962d31b481b6a153c23601c0f": {
                "636861726c69335f6164615f6e6674": 1
            },
            "8e51398904a5d3fc129fbf4f1589701de23c7824d5c90fdb9490e15a": {
                "434841524c4933": 1367726755
            },
            "d8d46a3e430fab5dc8c5a0a7fc82abbf4339a89034a8c804bb7e6012": {
                "636861726c69335f6164615f6c71": 9223372035870126880
            },
            "lovelace": 708864940,
        },
    },
    "16824312f4b2cb37c967bc604f70aac51a7c08173d3464996be2f082547b5098#1": {
        "address": "addr1v9p0rc57dzkz7gg97dmsns8hngsuxl956xe6myjldaug7hse4elc6",
        "datum": None,
        "datumhash": "55fe36f482e21ff6ae2caf2e33c3565572b568852dccd3f317ddecb91463d780",
        "inlineDatum": None,
        "referenceScript": {
            "script": {
                "cborHex": "5915fa5915f7010000323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232223232323232323232323232323232323232323232323232323232533533355333573460ee0082646464646424446666600201000e00c00a0086eb4d5d09aba25005375a6ae854010dd69aba15004375a6ae854010dd69aba1307d00515333573460ec008264646464646464244466666600401401201000e00a0086eb4d5d09aba2002375a6ae84004d5d128029bad35742a0086eb4d5d0a8021bad35742a0086eb4d5d0983e8028a999ab9a307500413212223003004375a6ae84c1f40141b08c8c8cc0d0ccc0d409803c040cc0d0cc0f0cc128068028cdc0806241a01e66068660786a02a0e4018660686607e01c90001981a1981f806a400066068666606c01e02001402e66068660786609403402c90011981a1981e1982500d004a400466068660786609402e01290011981a1a9a80d911103a911a80091912999aa999a80310a999a80210a999a804109802815098020148a999a802909802815098020148328338a999a803909802014898018140a999a802109802014898018140320a999a80190328318320a999a80190a999a803909802014898018140a999a802109802014898018140320330a999a803109801814098010138a999a801909801814098010138318a99a80083403503503412999a80110a999a80310a999a8021099981d0160010008b0b0b0330a999a80290a999a8019099981c8158010008b0b0b0328319981a1981f2805a40046606866080a0160fe66068607a02666068607a028607a02260d866610202444a666ae68cdc38011b8d004100113300333700004900119b803370400290400219b8e00400248001200033080012253350011622135002225333573466e3c00922011c91835de0e7ae8228a3e79823e8e066897f9c40e1b85c7a88c173a3e9001533500116221350022253350031002221613006003353353308001221225333573466e200052000130434910350543600153350021304349103505437002215333573460f80062004266a600c0d800266e0400d20020663501922222222222200c0012235001206a222223232322323303b33303c02d0160173303b3304333051021011337020269068079981d99823003a4000660766608c00c90001981d999981e80b00b80880f1981d998219982881080ea40046607666086660a204202090011981d998219982880f00824004660766608aa02490011981d99823a809043009981d982200d1981d982200d9981d982200c1981d998231aa80083824000660766608c6aa0020d29000198231aa800833a4000264a66aa66a66082002050264a66a66084002052260e4666080605000460500026aa008444a66a6608a002058266e0ccdc119b820063500107235500806f337046a0020de6aa0100e42c0d66aa0060d20d4420022c6aa0040de2646464a66a6a002446a00844666609a008006004002266607e660e401290011a800911a9982100280e111983b19b82004002337040060020022a66a6a002446a00844666605c008006004002266607e6a004446a6608460a400a60a403a44660ec66e08010008cdc10018009983900424004004266607e660e4012900119839004240040026a004446a038446a60a66608603c00c44660ee66e08cdc119b8200e0060040023370466e08c20c0401400c004d4c138cc0f800406088cc1c8cdc1004001183f00099981f801280080b899999982499837001a400400202c02e02802a660da00290011111911191981c19981c81500980a1981c1982180324000660706608600a90001981c199981d00980a00700d9981c198201982700f00d2400466070660806609c03c01a90011981c198201982700d806a40046607066084a01e90011981c198222807841809981c182080b9981c182080c1981c182080a9981c198219aa800835a4000660866aa0020d0900009919191919299aa99a99821000816099299a99821800816898399983a1a8010261a8008260361a801911a99821a80200e911983b99b82004002337040060020d6420022c6a004446a6608460a4a00660a403a44660ec66e08010008cdc1001800899982080300180ca999ab9a307d00116133070337046a0040d800800266e08008d40041a0cccccc124cc1b801520020030160170140153306b001480084480044c0f92410350543500135744a00226ae8940044d5d1183d001183d0009baa0173306235013223333500106920010690694890e4d7565736c69537761705f634c5000330614891c6e3af9667763e915c9b3a901d3092625d515c2ad6d575eac92582aa8003500c05a13500a06635007223500a2235009225333573460e40082c264a666ae68cdc399b8200330720013370466e04c1c8004cdc119b820070044800800854cd4cccc0f520004800801c01854cd4cccc0f401c0180140104d4cccccc104cc19802520023306600848008cc19801c018cc198014010cc19800c0080340f8585858cdc10028021981e8050019981e0048009a8030329a8028319a8021111102b1a801911110299a80110319a8009111102d1a80191112999a8010b10981d80090a99a9a8059111111111111983f11299a8008309109a801112999ab9a3371e004026260d80022600c0060044260780022c660d844a66a0022c4426a00444a666ae68cdc780101e8a99a981f091199820911a801112999ab9a306f0011330060040031003001003162213500222533500313305f0410022216130060030013500120535335303612233303922533535002222253335002053205620561330040020011001001003162215335001100222163500222222222222200a35001222205e3500104c5333573460b860ca00226464642466002006004607c6ae84d5d11833001a999ab9a305d3066001132323232323232323232323232323232323232323232321233333333333300101801601401201000e00c0090070050030023058357426ae88008ccc141d710009aba10013574400466609c0a040026ae84004d5d100119826bae357420026ae8800d4ccd5cd1836183a80089919191909198008020012999ab9a306f30780011330623304875a6ae84c1dc004c11cd5d09aba2307700106637546ae84d5d1183b001a999ab9a306d30760011323212330010030023046357426ae88c1d8008cc119d69aba1307500106437546ae84c1d000418cdd51aba10013574400466608e096eb4d5d08009aba200233046048357420026ae88008ccc10dd70211aba100135744004666082eb8100d5d08009aba20023304003c357420026ae88008cc0f80e4d5d08009aba230660023303c0373574260ca0020a86ea8d5d098320008299baa00123500122533533330270020014800120021533533330063370a004002002900024004266e00cdc2001000a4004266e1000800458cc129200048009262222333573466e24cdc100200099b82002003026047330474800120023333333300d017225333573466e1c0080040ec54ccd5cd19b8900200103c03e22333573466e2000800410c08806c068064894ccd5cd19b8900200110011002225333573466e2400800440084004cccccccc03088d401088888888d402888d402c894cd4cc0300100084ccd404417000c00412ccc00400800c894ccd4cccc00c0100140080040fc0fc104894ccd4cccc00c0100140080041040fc104894ccd4cccc00c0100140080040fc1040fc894ccd4cccc00c0100140080041041040fc894ccd4cccc00c010014008004400440084004894ccd4cccc00c0100140080044008400440088888d400888d400c8c894ccd4ccc05402401400c4ccc0540200100040080084ccc04c01c00c004cccccccc02801400802002401801c00c010cccccccc02401000401c02001401800800c894ccd5cd19b8f00200103615333573466e440080040dc0e4894ccd5cd19b9100200110011002225333573466e440080044008400488ccd5cd19b8f00200103b01a22333573466e440080040640e888ccd5cd19b9000200101803922333573466e400080040e005c88ccd5cd19b91002001037016222222221233333333001009008007006005004003002235001041225335002100103123500103e223232223232323253350041533550071333573460a2a0060740320020022a66a0060022a66aa00c2666ae68c13d40080e406000454cd400854cd540144ccd5cd1827a80081c00b8999ab9a3050500103801713335734609ea00207002e26666aa660a64422444a66a00226a006074442666a00a07e6008004666aa600e08000a0080020726607844666a0140740020046a01006a4466e00005200233305322253350011002221350022233007333305a22225335001100222135002225333573460b0002266601000e00c006266601000e6609866603000e00400200c00600400c00200606e0049000199ab9a3371266034002004900000a81b09a801912999ab9a3371e00491010015333573466e3c00522100034003003135001225333573466e3c009221001333573466e3c00522010003401303133034222300330020012001222123330010040030022235002223500322330383370266e08010004cdc100100199b82003001223500222350032233330100040030020012223500322350042235005223553335734608c0082c2646464246600200600466e0800800ccdc019b823370400e00800466e0800c004cdc100280201c91199ab9a3370e00400205801646a0024464a666ae68cdc38019a8008170999ab9a3370e0046a00205605a018054a666ae68c0f80044c01d24010350543300132330323370800600266e10008004ccc1208894ccd5cd1820800880109980180099b850020015333573466e2000920001303c00210025333573466e2000520001303c001100122333573466e200080040240a888ccd5cd19b8900200100802922333573466e240080040a001c94cd5ce0008b1111199ab9a3371066e08010004cdc100100181400391299a9999801801000a40009001099b84002001162222333573466e20cdc100200099b82002003005026101f22222232323232353300c004533357346078a0022c26605e601666e08d400c0ad4009400488d402088d4c044cc0cccdc124008004607e002446606a66e08018008cdc1002800899192999ab9a3371066e080040040084cdc0000a40042002601600266e08d400809d40044c8c8c8ccc11c8894ccd5cd19b8900148000520021337040046600600466e040052002480514ccd5cd19b89480000044004520003370200aa666ae68cdc48008010800880118189a80101518181a8008131a800911a804911a805111a80491198089981a19b820080083370400e00e6606866e08cdc119b8248020018010008cdc119b823040005003001350052235300b005223500a223500a2233010330333370401000c66e0801c014cc0cccdc100200119b8200300125333573466e200052000161533357346064002290000a999ab9a303300114800854ccd5cd181a0008a40042666078444a666ae68cdc400080109980180099b833370066e0c010004005200410020013370066e0c00520044800888d400888d400c88cc0a4cdc019b820040013370400400666e0800c0048d4004894ccd5cd18190010b099812800801111a800911981e1119a800a4000446a00444a666ae68cdc78010040998211119a800a4000446a00444a666ae68cdc7801006880089803001800898030018021192999ab9a302f303800113232323232323232323232323232123333333300100f00d00b009007005003002375a6ae84d5d10011a999807bad75a6ae84004894ccd5cd181e8008b0998180010009aba20023533300d75aeb4d5d0800912999ab9a303b0011613302e002001357440046a666016eb5d69aba1001225333573460720022c2660580040026ae88008dd69aba1001357440046eb4d5d08009aba200233300575ceb8d5d08009aba2303800233300375ceb8d5d0981b8008131baa00122232533357346060607200226604660086ae84c0e0004c00cd5d09aba2303800102737540029111c909133088303c49f3a30f1cc8ed553a73857a29779f6c6561cd8093f00233500101f019223035225335001100322133006002300400123253335734605600202e2a666ae68c0a8004054084c0c8dd50009119192999ab9a302d00101215333573460580022604060086ae84c0cc00854ccd5cd181580080a01118198009baa001232533357346050606200226464246600200600460086ae84d5d1181880118061aba1303000101f3754002464a666ae68c09cc0c00044c8c8c8c8c8c8c8c8c848cccc00402401c00c008cc02dd71aba135744008a666ae68c0c00044c84888c008010d5d0981b0010a999ab9a302f00113212223001004375c6ae84c0d800854ccd5cd181700080a012981b0009baa357420026ae88008ccc021d70039aba1001357446062006a666ae68c0a0c0c40044c8c848cc00400c008cc01402cd5d09aba23031002300b35742606000203e6ea8d5d0981780080f1baa0012232325333573460500022603460086ae84c0c000854ccd5cd181480080980f98180009baa0013300175ceb4888cc0bc88cccd55cf800900b1191980e9980e180398190009803181880098021aba20033574200402e6eac00488cc0b488cccd55cf800900a11980d18029aba100230033574400402a6eb00048c8c94ccd5cd181300089909111180200298021aba1302b002153335734604a00226424444600400a600a6ae84c0ac00854ccd5cd181200089909111180080298039aba1302b002153335734604600226424444600600a6eb8d5d0981580100d18158009baa0012323253335734605000222444402e2a666ae68c09c0044407c54ccd5cd18130008991909111111198008048041bad357426ae88c0ac00cdd71aba1302a002153335734604a0022646424444444660040120106eb8d5d09aba2302b003375c6ae84c0a800854ccd5cd18120008991909111111198030048041bae357426ae88c0ac00cc010d5d098150010a999ab9a302300113212222222300700830043574260540042a666ae68c0880044c848888888c014020c010d5d0981500100c98150009baa0012323253335734604400226464646424466600200c0080066eb4d5d09aba2002375a6ae84004d5d118150019bad3574260520042a666ae68c0840044c8488c00800cc010d5d0981480100c18148009baa0012323253335734604200226424460020066eb8d5d098140010a999ab9a30200011321223002003375c6ae84c0a000805cc0a0004dd50009192999ab9a301e3027001132321233001003002375a6ae84d5d1181380118019aba130260010153754002464a666ae68c074c0980044dd71aba1302500101437540022201622002444002220024440042200244002200220024400424002444006424460040064424660020060044424466002008006424446006008602844a666ae68c030004520001337009001180119b840014805054cd5ce2481035054310016253357389201024c680016222222220052222222200622222222007222222220082222222004370290001b8248008dc3a40006e1d2002370e90021b8748018dc3a40106e1d200a370e9006241413802aae7955ce9191800800911980198010010009",
                "description": "",
                "type": "PlutusScriptV2",
            },
            "scriptLanguage": "PlutusScriptLanguage PlutusScriptV2",
        },
        "value": {"lovelace": 25548890},
    },
}


@pytest.fixture
def chain_context(genesis_file, config_file):
    """
    Create a CardanoCliChainContext with a mock run_command method
    Args:
        genesis_file: The genesis file
        config_file: The config file

    Returns:
        The CardanoCliChainContext
    """

    def override_run_command_older_version(cmd: List[str]):
        """
        Override the run_command method of CardanoCliChainContext to return a mock result of older versions of cardano-cli.
        Args:
            cmd: The command to run

        Returns:
            The mock result
        """
        if "latest" in cmd:
            raise CardanoCliError(
                "Older versions of cardano-cli do not support the latest command"
            )
        if "tip" in cmd:
            return json.dumps(QUERY_TIP_RESULT)
        if "protocol-parameters" in cmd:
            return json.dumps(QUERY_PROTOCOL_PARAMETERS_RESULT)
        if "utxo" in cmd:
            return json.dumps(QUERY_UTXO_RESULT)
        if "txid" in cmd:
            return "270be16fa17cdb3ef683bf2c28259c978d4b7088792074f177c8efda247e23f7"
        if "version" in cmd:
            return "cardano-cli 8.1.2 - linux-x86_64 - ghc-8.10\ngit rev d2d90b48c5577b4412d5c9c9968b55f8ab4b9767"
        else:
            return None

    with patch(
        "pycardano.backend.cardano_cli.CardanoCliChainContext._run_command",
        side_effect=override_run_command_older_version,
    ):
        context = CardanoCliChainContext(
            binary=Path("cardano-cli"),
            socket=Path("node.socket"),
            config_file=config_file,
            network=CardanoCliNetwork.PREPROD,
        )
        context._run_command = override_run_command_older_version
    return context


@pytest.fixture
def chain_context_latest(genesis_file, config_file):
    """
    Create a CardanoCliChainContext with a mock run_command method
    Args:
        genesis_file: The genesis file
        config_file: The config file

    Returns:
        The CardanoCliChainContext
    """

    def override_run_command_latest(cmd: List[str]):
        """
        Override the run_command method of CardanoCliChainContext to return a mock result of the latest versions of cardano-cli.
        Args:
            cmd: The command to run

        Returns:
            The mock result
        """
        if "tip" in cmd:
            return json.dumps(QUERY_TIP_RESULT)
        if "txid" in cmd:
            return "270be16fa17cdb3ef683bf2c28259c978d4b7088792074f177c8efda247e23f7"
        else:
            return None

    with patch(
        "pycardano.backend.cardano_cli.CardanoCliChainContext._run_command",
        side_effect=override_run_command_latest,
    ):
        context = CardanoCliChainContext(
            binary=Path("cardano-cli"),
            socket=Path("node.socket"),
            config_file=config_file,
            network=CardanoCliNetwork.PREPROD,
        )
        context._run_command = override_run_command_latest
    return context


@pytest.fixture
def chain_context_tx_fail(genesis_file, config_file):
    """
    Create a CardanoCliChainContext with a mock run_command method
    Args:
        genesis_file: The genesis file
        config_file: The config file

    Returns:
        The CardanoCliChainContext
    """

    def override_run_command_fail(cmd: List[str]):
        if "transaction" in cmd:
            raise CardanoCliError("Intentionally raised error for testing purposes")
        if "tip" in cmd:
            return json.dumps(QUERY_TIP_RESULT)
        return None

    with patch(
        "pycardano.backend.cardano_cli.CardanoCliChainContext._run_command",
        side_effect=override_run_command_fail,
    ):
        context = CardanoCliChainContext(
            binary=Path("cardano-cli"),
            socket=Path("node.socket"),
            config_file=config_file,
            network=CardanoCliNetwork.PREPROD,
        )
        context._run_command = override_run_command_fail
    return context


@pytest.fixture
def chain_context_tx_id_fail(genesis_file, config_file):
    """
    Create a CardanoCliChainContext with a mock run_command method
    Args:
        genesis_file: The genesis file
        config_file: The config file

    Returns:
        The CardanoCliChainContext
    """

    def override_run_command_fail(cmd: List[str]):
        if "txid" in cmd:
            raise CardanoCliError("Intentionally raised error for testing purposes")
        if "tip" in cmd:
            return json.dumps(QUERY_TIP_RESULT)
        return None

    with patch(
        "pycardano.backend.cardano_cli.CardanoCliChainContext._run_command",
        side_effect=override_run_command_fail,
    ):
        context = CardanoCliChainContext(
            binary=Path("cardano-cli"),
            socket=Path("node.socket"),
            config_file=config_file,
            network=CardanoCliNetwork.PREPROD,
        )
        context._run_command = override_run_command_fail
    return context


def test_network_magic():
    assert network_magic(1) == ["--testnet-magic", "1"]


class TestCardanoCliChainContext:
    def test_protocol_param(self, chain_context):
        assert (
            ProtocolParameters(
                min_fee_constant=QUERY_PROTOCOL_PARAMETERS_RESULT["txFeeFixed"],
                min_fee_coefficient=QUERY_PROTOCOL_PARAMETERS_RESULT["txFeePerByte"],
                max_block_size=QUERY_PROTOCOL_PARAMETERS_RESULT["maxBlockBodySize"],
                max_tx_size=QUERY_PROTOCOL_PARAMETERS_RESULT["maxTxSize"],
                max_block_header_size=QUERY_PROTOCOL_PARAMETERS_RESULT[
                    "maxBlockHeaderSize"
                ],
                key_deposit=QUERY_PROTOCOL_PARAMETERS_RESULT["stakeAddressDeposit"],
                pool_deposit=QUERY_PROTOCOL_PARAMETERS_RESULT["stakePoolDeposit"],
                pool_influence=QUERY_PROTOCOL_PARAMETERS_RESULT["poolPledgeInfluence"],
                monetary_expansion=QUERY_PROTOCOL_PARAMETERS_RESULT[
                    "monetaryExpansion"
                ],
                treasury_expansion=QUERY_PROTOCOL_PARAMETERS_RESULT["treasuryCut"],
                decentralization_param=QUERY_PROTOCOL_PARAMETERS_RESULT.get(
                    "decentralization", 0
                ),
                extra_entropy=QUERY_PROTOCOL_PARAMETERS_RESULT.get(
                    "extraPraosEntropy", ""
                ),
                protocol_major_version=int(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["protocolVersion"]["major"]
                ),
                protocol_minor_version=int(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["protocolVersion"]["minor"]
                ),
                min_utxo=QUERY_PROTOCOL_PARAMETERS_RESULT.get(
                    "minUTxOValue",
                    QUERY_PROTOCOL_PARAMETERS_RESULT.get("lovelacePerUTxOWord", 0),
                )
                or 0,
                min_pool_cost=QUERY_PROTOCOL_PARAMETERS_RESULT["minPoolCost"],
                price_mem=float(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["executionUnitPrices"][
                        "priceMemory"
                    ]
                ),
                price_step=float(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["executionUnitPrices"][
                        "priceSteps"
                    ]
                ),
                max_tx_ex_mem=int(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["maxTxExecutionUnits"]["memory"]
                ),
                max_tx_ex_steps=int(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["maxTxExecutionUnits"]["steps"]
                ),
                max_block_ex_mem=int(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["maxBlockExecutionUnits"]["memory"]
                ),
                max_block_ex_steps=int(
                    QUERY_PROTOCOL_PARAMETERS_RESULT["maxBlockExecutionUnits"]["steps"]
                ),
                max_val_size=QUERY_PROTOCOL_PARAMETERS_RESULT["maxValueSize"],
                collateral_percent=QUERY_PROTOCOL_PARAMETERS_RESULT[
                    "collateralPercentage"
                ],
                max_collateral_inputs=QUERY_PROTOCOL_PARAMETERS_RESULT[
                    "maxCollateralInputs"
                ],
                coins_per_utxo_word=QUERY_PROTOCOL_PARAMETERS_RESULT.get(
                    "coinsPerUtxoWord", ALONZO_COINS_PER_UTXO_WORD
                ),
                coins_per_utxo_byte=QUERY_PROTOCOL_PARAMETERS_RESULT.get(
                    "coinsPerUtxoByte",
                    QUERY_PROTOCOL_PARAMETERS_RESULT.get("utxoCostPerByte", 0),
                ),
                cost_models={
                    l: {
                        i: v
                        for i, v in enumerate(
                            QUERY_PROTOCOL_PARAMETERS_RESULT["costModels"][l]
                        )
                    }
                    for l in QUERY_PROTOCOL_PARAMETERS_RESULT["costModels"]
                },
            )
            == chain_context.protocol_param
        )

    def test_genesis(self, chain_context, genesis_json):
        assert (
            GenesisParameters(
                active_slots_coefficient=genesis_json["activeSlotsCoeff"],
                update_quorum=genesis_json["updateQuorum"],
                max_lovelace_supply=genesis_json["maxLovelaceSupply"],
                network_magic=genesis_json["networkMagic"],
                epoch_length=genesis_json["epochLength"],
                system_start=genesis_json["systemStart"],
                slots_per_kes_period=genesis_json["slotsPerKESPeriod"],
                slot_length=genesis_json["slotLength"],
                max_kes_evolutions=genesis_json["maxKESEvolutions"],
                security_param=genesis_json["securityParam"],
            )
            == chain_context.genesis_param
        )

    def test_version(self, chain_context):
        assert (
            chain_context.version()
            == "cardano-cli 8.1.2 - linux-x86_64 - ghc-8.10\ngit rev d2d90b48c5577b4412d5c9c9968b55f8ab4b9767"
        )

    def test_utxo(self, chain_context):
        results = chain_context.utxos(
            "addr_test1qqmnh90jyfaajul4h2mawrxz4rfx04hpaadstm6y8wr90kyhf4dqfm247jlvna83g5wx9veaymzl6g9t833grknh3yhqxhzh4n"
        )

        assert results[0].input == TransactionInput.from_primitive(
            ["fbaa018740241abb935240051134914389c3f94647d8bd6c30cb32d3fdb799bf", 0]
        )
        assert results[0].output.amount.coin == 708864940

        assert (
            str(results[0].output.address)
            == "addr1x8nz307k3sr60gu0e47cmajssy4fmld7u493a4xztjrll0aj764lvrxdayh2ux30fl0ktuh27csgmpevdu89jlxppvrswgxsta"
        )

        assert results[0].output.datum == RawPlutusData.from_dict(
            {
                "constructor": 0,
                "fields": [
                    {
                        "constructor": 0,
                        "fields": [
                            {
                                "bytes": "2e11e7313e00ccd086cfc4f1c3ebed4962d31b481b6a153c23601c0f"
                            },
                            {"bytes": "636861726c69335f6164615f6e6674"},
                        ],
                    },
                    {"constructor": 0, "fields": [{"bytes": ""}, {"bytes": ""}]},
                    {
                        "constructor": 0,
                        "fields": [
                            {
                                "bytes": "8e51398904a5d3fc129fbf4f1589701de23c7824d5c90fdb9490e15a"
                            },
                            {"bytes": "434841524c4933"},
                        ],
                    },
                    {
                        "constructor": 0,
                        "fields": [
                            {
                                "bytes": "d8d46a3e430fab5dc8c5a0a7fc82abbf4339a89034a8c804bb7e6012"
                            },
                            {"bytes": "636861726c69335f6164615f6c71"},
                        ],
                    },
                    {"int": 997},
                    {
                        "list": [
                            {
                                "bytes": "4dd98a2ef34bc7ac3858bbcfdf94aaa116bb28ca7e01756140ba4d19"
                            }
                        ]
                    },
                    {"int": 10000000000},
                ],
            }
        )

        assert results[0].output.amount.multi_asset == MultiAsset.from_primitive(
            {
                "2e11e7313e00ccd086cfc4f1c3ebed4962d31b481b6a153c23601c0f": {
                    "636861726c69335f6164615f6e6674": 1
                },
                "8e51398904a5d3fc129fbf4f1589701de23c7824d5c90fdb9490e15a": {
                    "434841524c4933": 1367726755
                },
                "d8d46a3e430fab5dc8c5a0a7fc82abbf4339a89034a8c804bb7e6012": {
                    "636861726c69335f6164615f6c71": 9223372035870126880
                },
            }
        )

        assert results[1].output.script == PlutusV2Script(
            bytes.fromhex(
                "5915f7010000323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232223232323232323232323232323232323232323232323232323232533533355333573460ee0082646464646424446666600201000e00c00a0086eb4d5d09aba25005375a6ae854010dd69aba15004375a6ae854010dd69aba1307d00515333573460ec008264646464646464244466666600401401201000e00a0086eb4d5d09aba2002375a6ae84004d5d128029bad35742a0086eb4d5d0a8021bad35742a0086eb4d5d0983e8028a999ab9a307500413212223003004375a6ae84c1f40141b08c8c8cc0d0ccc0d409803c040cc0d0cc0f0cc128068028cdc0806241a01e66068660786a02a0e4018660686607e01c90001981a1981f806a400066068666606c01e02001402e66068660786609403402c90011981a1981e1982500d004a400466068660786609402e01290011981a1a9a80d911103a911a80091912999aa999a80310a999a80210a999a804109802815098020148a999a802909802815098020148328338a999a803909802014898018140a999a802109802014898018140320a999a80190328318320a999a80190a999a803909802014898018140a999a802109802014898018140320330a999a803109801814098010138a999a801909801814098010138318a99a80083403503503412999a80110a999a80310a999a8021099981d0160010008b0b0b0330a999a80290a999a8019099981c8158010008b0b0b0328319981a1981f2805a40046606866080a0160fe66068607a02666068607a028607a02260d866610202444a666ae68cdc38011b8d004100113300333700004900119b803370400290400219b8e00400248001200033080012253350011622135002225333573466e3c00922011c91835de0e7ae8228a3e79823e8e066897f9c40e1b85c7a88c173a3e9001533500116221350022253350031002221613006003353353308001221225333573466e200052000130434910350543600153350021304349103505437002215333573460f80062004266a600c0d800266e0400d20020663501922222222222200c0012235001206a222223232322323303b33303c02d0160173303b3304333051021011337020269068079981d99823003a4000660766608c00c90001981d999981e80b00b80880f1981d998219982881080ea40046607666086660a204202090011981d998219982880f00824004660766608aa02490011981d99823a809043009981d982200d1981d982200d9981d982200c1981d998231aa80083824000660766608c6aa0020d29000198231aa800833a4000264a66aa66a66082002050264a66a66084002052260e4666080605000460500026aa008444a66a6608a002058266e0ccdc119b820063500107235500806f337046a0020de6aa0100e42c0d66aa0060d20d4420022c6aa0040de2646464a66a6a002446a00844666609a008006004002266607e660e401290011a800911a9982100280e111983b19b82004002337040060020022a66a6a002446a00844666605c008006004002266607e6a004446a6608460a400a60a403a44660ec66e08010008cdc10018009983900424004004266607e660e4012900119839004240040026a004446a038446a60a66608603c00c44660ee66e08cdc119b8200e0060040023370466e08c20c0401400c004d4c138cc0f800406088cc1c8cdc1004001183f00099981f801280080b899999982499837001a400400202c02e02802a660da00290011111911191981c19981c81500980a1981c1982180324000660706608600a90001981c199981d00980a00700d9981c198201982700f00d2400466070660806609c03c01a90011981c198201982700d806a40046607066084a01e90011981c198222807841809981c182080b9981c182080c1981c182080a9981c198219aa800835a4000660866aa0020d0900009919191919299aa99a99821000816099299a99821800816898399983a1a8010261a8008260361a801911a99821a80200e911983b99b82004002337040060020d6420022c6a004446a6608460a4a00660a403a44660ec66e08010008cdc1001800899982080300180ca999ab9a307d00116133070337046a0040d800800266e08008d40041a0cccccc124cc1b801520020030160170140153306b001480084480044c0f92410350543500135744a00226ae8940044d5d1183d001183d0009baa0173306235013223333500106920010690694890e4d7565736c69537761705f634c5000330614891c6e3af9667763e915c9b3a901d3092625d515c2ad6d575eac92582aa8003500c05a13500a06635007223500a2235009225333573460e40082c264a666ae68cdc399b8200330720013370466e04c1c8004cdc119b820070044800800854cd4cccc0f520004800801c01854cd4cccc0f401c0180140104d4cccccc104cc19802520023306600848008cc19801c018cc198014010cc19800c0080340f8585858cdc10028021981e8050019981e0048009a8030329a8028319a8021111102b1a801911110299a80110319a8009111102d1a80191112999a8010b10981d80090a99a9a8059111111111111983f11299a8008309109a801112999ab9a3371e004026260d80022600c0060044260780022c660d844a66a0022c4426a00444a666ae68cdc780101e8a99a981f091199820911a801112999ab9a306f0011330060040031003001003162213500222533500313305f0410022216130060030013500120535335303612233303922533535002222253335002053205620561330040020011001001003162215335001100222163500222222222222200a35001222205e3500104c5333573460b860ca00226464642466002006004607c6ae84d5d11833001a999ab9a305d3066001132323232323232323232323232323232323232323232321233333333333300101801601401201000e00c0090070050030023058357426ae88008ccc141d710009aba10013574400466609c0a040026ae84004d5d100119826bae357420026ae8800d4ccd5cd1836183a80089919191909198008020012999ab9a306f30780011330623304875a6ae84c1dc004c11cd5d09aba2307700106637546ae84d5d1183b001a999ab9a306d30760011323212330010030023046357426ae88c1d8008cc119d69aba1307500106437546ae84c1d000418cdd51aba10013574400466608e096eb4d5d08009aba200233046048357420026ae88008ccc10dd70211aba100135744004666082eb8100d5d08009aba20023304003c357420026ae88008cc0f80e4d5d08009aba230660023303c0373574260ca0020a86ea8d5d098320008299baa00123500122533533330270020014800120021533533330063370a004002002900024004266e00cdc2001000a4004266e1000800458cc129200048009262222333573466e24cdc100200099b82002003026047330474800120023333333300d017225333573466e1c0080040ec54ccd5cd19b8900200103c03e22333573466e2000800410c08806c068064894ccd5cd19b8900200110011002225333573466e2400800440084004cccccccc03088d401088888888d402888d402c894cd4cc0300100084ccd404417000c00412ccc00400800c894ccd4cccc00c0100140080040fc0fc104894ccd4cccc00c0100140080041040fc104894ccd4cccc00c0100140080040fc1040fc894ccd4cccc00c0100140080041041040fc894ccd4cccc00c010014008004400440084004894ccd4cccc00c0100140080044008400440088888d400888d400c8c894ccd4ccc05402401400c4ccc0540200100040080084ccc04c01c00c004cccccccc02801400802002401801c00c010cccccccc02401000401c02001401800800c894ccd5cd19b8f00200103615333573466e440080040dc0e4894ccd5cd19b9100200110011002225333573466e440080044008400488ccd5cd19b8f00200103b01a22333573466e440080040640e888ccd5cd19b9000200101803922333573466e400080040e005c88ccd5cd19b91002001037016222222221233333333001009008007006005004003002235001041225335002100103123500103e223232223232323253350041533550071333573460a2a0060740320020022a66a0060022a66aa00c2666ae68c13d40080e406000454cd400854cd540144ccd5cd1827a80081c00b8999ab9a3050500103801713335734609ea00207002e26666aa660a64422444a66a00226a006074442666a00a07e6008004666aa600e08000a0080020726607844666a0140740020046a01006a4466e00005200233305322253350011002221350022233007333305a22225335001100222135002225333573460b0002266601000e00c006266601000e6609866603000e00400200c00600400c00200606e0049000199ab9a3371266034002004900000a81b09a801912999ab9a3371e00491010015333573466e3c00522100034003003135001225333573466e3c009221001333573466e3c00522010003401303133034222300330020012001222123330010040030022235002223500322330383370266e08010004cdc100100199b82003001223500222350032233330100040030020012223500322350042235005223553335734608c0082c2646464246600200600466e0800800ccdc019b823370400e00800466e0800c004cdc100280201c91199ab9a3370e00400205801646a0024464a666ae68cdc38019a8008170999ab9a3370e0046a00205605a018054a666ae68c0f80044c01d24010350543300132330323370800600266e10008004ccc1208894ccd5cd1820800880109980180099b850020015333573466e2000920001303c00210025333573466e2000520001303c001100122333573466e200080040240a888ccd5cd19b8900200100802922333573466e240080040a001c94cd5ce0008b1111199ab9a3371066e08010004cdc100100181400391299a9999801801000a40009001099b84002001162222333573466e20cdc100200099b82002003005026101f22222232323232353300c004533357346078a0022c26605e601666e08d400c0ad4009400488d402088d4c044cc0cccdc124008004607e002446606a66e08018008cdc1002800899192999ab9a3371066e080040040084cdc0000a40042002601600266e08d400809d40044c8c8c8ccc11c8894ccd5cd19b8900148000520021337040046600600466e040052002480514ccd5cd19b89480000044004520003370200aa666ae68cdc48008010800880118189a80101518181a8008131a800911a804911a805111a80491198089981a19b820080083370400e00e6606866e08cdc119b8248020018010008cdc119b823040005003001350052235300b005223500a223500a2233010330333370401000c66e0801c014cc0cccdc100200119b8200300125333573466e200052000161533357346064002290000a999ab9a303300114800854ccd5cd181a0008a40042666078444a666ae68cdc400080109980180099b833370066e0c010004005200410020013370066e0c00520044800888d400888d400c88cc0a4cdc019b820040013370400400666e0800c0048d4004894ccd5cd18190010b099812800801111a800911981e1119a800a4000446a00444a666ae68cdc78010040998211119a800a4000446a00444a666ae68cdc7801006880089803001800898030018021192999ab9a302f303800113232323232323232323232323232123333333300100f00d00b009007005003002375a6ae84d5d10011a999807bad75a6ae84004894ccd5cd181e8008b0998180010009aba20023533300d75aeb4d5d0800912999ab9a303b0011613302e002001357440046a666016eb5d69aba1001225333573460720022c2660580040026ae88008dd69aba1001357440046eb4d5d08009aba200233300575ceb8d5d08009aba2303800233300375ceb8d5d0981b8008131baa00122232533357346060607200226604660086ae84c0e0004c00cd5d09aba2303800102737540029111c909133088303c49f3a30f1cc8ed553a73857a29779f6c6561cd8093f00233500101f019223035225335001100322133006002300400123253335734605600202e2a666ae68c0a8004054084c0c8dd50009119192999ab9a302d00101215333573460580022604060086ae84c0cc00854ccd5cd181580080a01118198009baa001232533357346050606200226464246600200600460086ae84d5d1181880118061aba1303000101f3754002464a666ae68c09cc0c00044c8c8c8c8c8c8c8c8c848cccc00402401c00c008cc02dd71aba135744008a666ae68c0c00044c84888c008010d5d0981b0010a999ab9a302f00113212223001004375c6ae84c0d800854ccd5cd181700080a012981b0009baa357420026ae88008ccc021d70039aba1001357446062006a666ae68c0a0c0c40044c8c848cc00400c008cc01402cd5d09aba23031002300b35742606000203e6ea8d5d0981780080f1baa0012232325333573460500022603460086ae84c0c000854ccd5cd181480080980f98180009baa0013300175ceb4888cc0bc88cccd55cf800900b1191980e9980e180398190009803181880098021aba20033574200402e6eac00488cc0b488cccd55cf800900a11980d18029aba100230033574400402a6eb00048c8c94ccd5cd181300089909111180200298021aba1302b002153335734604a00226424444600400a600a6ae84c0ac00854ccd5cd181200089909111180080298039aba1302b002153335734604600226424444600600a6eb8d5d0981580100d18158009baa0012323253335734605000222444402e2a666ae68c09c0044407c54ccd5cd18130008991909111111198008048041bad357426ae88c0ac00cdd71aba1302a002153335734604a0022646424444444660040120106eb8d5d09aba2302b003375c6ae84c0a800854ccd5cd18120008991909111111198030048041bae357426ae88c0ac00cc010d5d098150010a999ab9a302300113212222222300700830043574260540042a666ae68c0880044c848888888c014020c010d5d0981500100c98150009baa0012323253335734604400226464646424466600200c0080066eb4d5d09aba2002375a6ae84004d5d118150019bad3574260520042a666ae68c0840044c8488c00800cc010d5d0981480100c18148009baa0012323253335734604200226424460020066eb8d5d098140010a999ab9a30200011321223002003375c6ae84c0a000805cc0a0004dd50009192999ab9a301e3027001132321233001003002375a6ae84d5d1181380118019aba130260010153754002464a666ae68c074c0980044dd71aba1302500101437540022201622002444002220024440042200244002200220024400424002444006424460040064424660020060044424466002008006424446006008602844a666ae68c030004520001337009001180119b840014805054cd5ce2481035054310016253357389201024c680016222222220052222222200622222222007222222220082222222004370290001b8248008dc3a40006e1d2002370e90021b8748018dc3a40106e1d200a370e9006241413802aae7955ce9191800800911980198010010009"
            )
        )
        assert results[1].output.datum_hash == DatumHash.from_primitive(
            "55fe36f482e21ff6ae2caf2e33c3565572b568852dccd3f317ddecb91463d780"
        )

    def test_submit_tx_bytes(self, chain_context):
        results = chain_context.submit_tx("testcborhexfromtransaction".encode("utf-8"))

        assert (
            results
            == "270be16fa17cdb3ef683bf2c28259c978d4b7088792074f177c8efda247e23f7"
        )

    def test_submit_tx(self, chain_context):
        results = chain_context.submit_tx("testcborhexfromtransaction")

        assert (
            results
            == "270be16fa17cdb3ef683bf2c28259c978d4b7088792074f177c8efda247e23f7"
        )

    def test_submit_tx_latest(self, chain_context_latest):
        results = chain_context_latest.submit_tx("testcborhexfromtransaction")

        assert (
            results
            == "270be16fa17cdb3ef683bf2c28259c978d4b7088792074f177c8efda247e23f7"
        )

    def test_submit_tx_fail(self, chain_context_tx_fail):
        with pytest.raises(TransactionFailedException) as exc_info:
            chain_context_tx_fail.submit_tx("testcborhexfromtransaction")
        assert str(exc_info.value) == "Failed to submit transaction"

    def test_submit_tx_id_fail(self, chain_context_tx_id_fail):
        with pytest.raises(PyCardanoException) as exc_info:
            chain_context_tx_id_fail.submit_tx("testcborhexfromtransaction")
        assert str(exc_info.value).startswith("Unable to get transaction id for")

    def test_epoch(self, chain_context):
        assert chain_context.epoch == 98
