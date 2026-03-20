def drawASCII_test():
    # Simulate the JS tabData
    tabData = [
        {"string": 4, "fret": 12, "modifier": None},
        {"string": 3, "fret": 9, "modifier": None},
        {"string": 3, "fret": 10, "modifier": None},
        {"string": 3, "fret": 12, "modifier": None},
        {"string": 2, "fret": 10, "modifier": None},
        {"string": 2, "fret": 11, "modifier": None},
        {"string": 2, "fret": 10, "modifier": None},
        {"string": 2, "fret": 11, "modifier": None},
        {"string": 2, "fret": 10, "modifier": None},
        {"string": 3, "fret": 12, "modifier": None},
        {"string": 3, "fret": 10, "modifier": None},
        {"string": 3, "fret": 9, "modifier": None},
        {"string": 4, "fret": 12, "modifier": None}
    ]

    strings = {
        1: "e|---", 2: "B|---", 3: "G|---", 4: "D|---", 5: "A|---", 6: "E|---"
    }

    for idx, pos in enumerate(tabData):
        fretStr = str(pos["fret"])
        isSlideNext = (idx + 1 < len(tabData) and tabData[idx + 1].get("modifier") == '/')
        
        for i in range(1, 7):
            if i == pos["string"]:
                if pos.get("modifier") == '/':
                    strings[i] += "/" + fretStr
                else:
                    strings[i] += "-" + fretStr
                if not isSlideNext:
                    strings[i] += "-"
            else:
                addedWidth = len(fretStr) + 1
                strings[i] += "-" * addedWidth
                if not isSlideNext:
                    strings[i] += "-"

    out = []
    for i in range(1, 7):
        line = strings[i] + "---|"
        out.append(line)
        print(f"String {i} Length: {len(line)} | Content: {line}")

drawASCII_test()
