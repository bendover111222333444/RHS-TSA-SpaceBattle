from lib.window_arena import *
from lib.winobj_ship import *
from typing import List

# update ship (this is where your code goes)
def updateShipLiam(ship: Ship, powerUps: List[PowerUp], targets: List[Target]):

    ship.setPlayerName("Liam C")

    shipAmmoSpeed = Ammo.SPEED #(units per second)
    shipAmmoDistance = ship.ammoMaxRange # (units)
    shipRotationSpeed = ship.shipTurnSpeed # (degrees per second)
    shipMoveSpeed = ship.shipMoveSpeed # (units per second)
    
    enoughAmmo = 10 # more than this = shoot
    shipAmmoBuffer = 2
    bufferedAmmoDistance = shipAmmoDistance - shipAmmoBuffer

    shipRad = math.atan2(ship.dir[1], ship.dir[0])
    shipAng= math.degrees(shipRad)

    ship.calcAng = shipAng
    ship.calcPos = [ship.pos[0], ship.pos[1]]

    #finds distance between two x and y differences
    def findDistance(diff):
        return math.sqrt(math.pow(diff[0], 2) + math.pow(diff[1], 2))
    
    def normalizeVec2(vector2, normalizeVal):
        vector2[0] = vector2[0] / normalizeVal
        vector2[1] = vector2[1] / normalizeVal
        return vector2

    def diffVec2(startPos, endPos):
        xDiff = endPos[0] - startPos[0]
        yDiff = endPos[1] - startPos[1]
        return [xDiff, yDiff]

    # use these for specific cases where sorting requires getting the score
    def getValue(item):
        return item["value"]
    
    def getType(item):
        return item["type"]

    def calcAng(diff, startAng, trueAng = False):

        inputRad = math.atan2(diff[1], diff[0])
        outputAng = startAng - math.degrees(inputRad)

        if trueAng == True: return outputAng

        #better angle could be found
        possBetterAng1 = (outputAng - 360)
        possBetterAng2 = (outputAng + 360)

        if abs(possBetterAng1) < abs(outputAng):
            outputAng = possBetterAng1
        if abs(possBetterAng2) < abs(outputAng):
            outputAng = possBetterAng2

        return outputAng

    # only needs initalPos and initalVel
    def predictTarget(initalPos, initalVel, initalTime = 2, exitVal = 0.001, maxDepth = 100):
        #predicts where target will be after a certain amount of time is recursive (kind of not really anymore) as to account for changes each time
        
        finalTime = initalTime

        posX, posY = initalPos[0], initalPos[1]
        velX, velY = initalVel[0], initalVel[1]

        # le recursive loop for time (split into later func if needed)

        for _ in range(maxDepth):

            predictedXPos = posX + (velX * finalTime)
            predictedYPos = posY + (velY * finalTime)
            
            predictedPos = [predictedXPos, predictedYPos]
            predictedDiff = diffVec2(ship.calcPos, predictedPos)
            distTargetPredicted = findDistance(predictedDiff)
            
            calcuatedAng = calcAng(predictedDiff, ship.calcAng)
            absAng = abs(calcuatedAng)

            moveDist = (distTargetPredicted - bufferedAmmoDistance)
            moveTime = max(0, moveDist / shipMoveSpeed)
            
            bulletTime = bufferedAmmoDistance / shipAmmoSpeed
            if (distTargetPredicted < shipAmmoDistance):
                bulletTime = distTargetPredicted / shipAmmoSpeed

            rotTime = absAng / shipRotationSpeed

            newTime = moveTime + rotTime + bulletTime

            if ((abs(newTime - finalTime) <= exitVal)):
                finalTime = newTime
                break

            finalTime = newTime

        finalXPos = posX + (velX * finalTime)
        finalYPos = posY + (velY * finalTime)

        finalPos = [finalXPos, finalYPos]

        finalDiff = diffVec2(ship.calcPos, finalPos)
        distTargetFinal = findDistance(finalDiff)
        
        circleX, circleY = finalXPos, finalYPos
        if (distTargetFinal > bufferedAmmoDistance):

            normalizedVector = normalizeVec2(finalDiff, distTargetFinal)
            circleX -= (normalizedVector[0] * bufferedAmmoDistance)
            circleY -= (normalizedVector[1] * bufferedAmmoDistance)

        outputVec = diffVec2(ship.calcPos, [circleX, circleY])
        outputAngle = calcAng(outputVec, ship.calcAng)
        
        return outputVec, outputAngle, distTargetFinal, finalPos
    windowBuffer = 0.5
    def inArena(pos):
        w = ship.window
        withinX = pos[0] > w.minCoordinateX() + windowBuffer and pos[0] < w.maxCoordinateX() - windowBuffer
        withinY = pos[1] > w.minCoordinateY() + windowBuffer and pos[1] < w.maxCoordinateY() - windowBuffer
        
        return withinX and withinY

    def targetsArena(targetDict):
        reachableTargets = []
        for entry in targetDict:
            target = entry["target"]
            predictedPos = predictTarget(target.pos, target.vel)[3]
            if inArena(predictedPos):
                reachableTargets.append(entry)
        return reachableTargets

    def moveTo(diff, angle):

        absoluteAng = abs(angle)

        dist = findDistance(diff)

        if (dist < 0.15):
            return

        if angle > 0:
            ship.queueCommand( ShipCmd_ThrustLeft(absoluteAng), False)
        else:
            ship.queueCommand( ShipCmd_ThrustRight(absoluteAng), False)
        
        ship.queueCommand( ShipCmd_Thrust(dist), False)

    def findBest(targetDict, amount):

        targetDict.sort(key=getValue, reverse=True)

        newTargets = []

        for index in range(amount):
            newTargets.append(targetDict[index])

        return newTargets
    
    def createDicts(targets, powerups):
        
        targetDict = []
        powerupDict = []
        for target in targets:
            targetDict.append({
                "target" : target,
                "type" : "target",
                "value" : 1
            })
        otherShip = ship.getOther()
        if (otherShip != None):
            targetDict.append({
                "target" : otherShip,
                "type" : "target",
                "value" : 0.6
            })
        for powerup in powerups:
            powerupDict.append({
                "powerUp" : powerup,
                "type" : "powerUp",
                "value" : 1
            })
        return targetDict, powerupDict

    distBaseVal = 1
    distReciprocalMulti = 20

    def categorizeDistance(targetDict, powerupDict ):
        for entry in targetDict:
 
            entryPos = entry["target"].pos

            diff = diffVec2(ship.pos, entryPos)
            dist = findDistance(diff)
            if (dist == 0):
                dist = 0.001
            
            entry["value"] *= distBaseVal + (1/dist) * distReciprocalMulti
            
        for entry in powerupDict:

            entryPos = entry["powerUp"].pos

            diff = diffVec2(ship.pos, entryPos)
            dist = findDistance(diff)
            if (dist == 0):
                dist = 0.001
            
            entry["value"] *= distBaseVal + (1/dist) * distReciprocalMulti
        return targetDict, powerupDict

    powerupValues = {
        "P" : 1.1,
        "S" : 200/(180 - ship.window.levelTime), #lowers throughout game
        "R" : 0.4,
        "3" : 2.0,
        "2" : 1.5,
        "1" : 0.8
    }
    
    # call function is
    # categorizePowerupUsefullness(categorizeDistance()[1]) <--- 2am sleepy guy
    def categorizePowerupUsefulness(powerupDict):

        for entry in powerupDict:

            if (entry["powerUp"].type == "P"):

                entry["value"] *= powerupValues["P"]

            elif (entry["powerUp"].type == "S"):

                entry["value"] *= powerupValues["S"]

            elif (entry["powerUp"].type == "R"):

                entry["value"] *= powerupValues["R"]

            elif (entry["powerUp"].type == "3"):

                entry["value"] *= powerupValues["3"]

            elif (entry["powerUp"].type == "2"):

                entry["value"] *= powerupValues["2"]

            elif (entry["powerUp"].type == "1"):

                entry["value"] *= powerupValues["1"]

        return powerupDict 

    proximityMulti = 0.4
    
    def catizgorizeProximityToOther(targetDict, powerupDict):

        for entry in targetDict:

            for entry2 in targetDict:

                diff = diffVec2(entry["target"].pos, entry2["target"].pos)

                dist = findDistance(diff)
            
                if (dist == 0):
                    dist = 0.001

                entry["value"] *= distBaseVal + ((1/dist) * distReciprocalMulti) * proximityMulti
                
        for entry in powerupDict:

            for entry2 in targetDict:
                
                diff = diffVec2(entry["powerUp"].pos, entry2["target"].pos)

                dist = findDistance(diff)

                if (dist == 0):
                    dist = 0.001

                entry["value"] *= distBaseVal + ((1/dist) * distReciprocalMulti) * proximityMulti

        return targetDict, powerupDict
        #scan around a radius around each and check if more things ther e
    baseRotSlope = 0.1
    def categorizeRotation(targetDict, powerupDict):
        
        for entry in targetDict:
            targetPos = entry["target"].pos
            diff = diffVec2(ship.pos, targetPos)
            ang = abs(ship.calcAng - calcAng(diff, ship.calcAng))
            
            entry["value"] *= baseRotSlope * (1/2 * (math.cos((ang*math.pi) / 180)) + 0.5)
        
        for entry in powerupDict:
            targetPos = entry["powerUp"].pos
            diff = diffVec2(ship.pos, targetPos)
            ang = abs(ship.calcAng - calcAng(diff, ship.calcAng))
            
            entry["value"] *= baseRotSlope * (1/2 * (math.cos((ang*math.pi) / 180)) + 0.5)

        return targetDict, powerupDict
            
    def categorizeAmmo(targetDict):
        for entry in targetDict:
            entry["value"] *= math.pow(ship.ammo, 2) * (1/(math.pow(enoughAmmo, 2)))
        return targetDict
    
    def shootEnemy(target):

        predictedVector, predictedAngle, predictedDist, _ = predictTarget(target.pos, target.vel)
        
        if predictedDist > (shipAmmoDistance - shipAmmoBuffer):

            moveTo(predictedVector, predictedAngle)
            return
        else:
        
            ship.queueCommand( ShipCmd_Shoot(normalizeVec2(predictedVector, predictedDist)), False)
            

    targetDict, powerUpDict = createDicts(targets, powerUps)
    targetDict = targetsArena(targetDict) #filters out unreachable targets (they go off map)
    targetDict, powerUpDict = categorizeDistance(targetDict, powerUpDict)
    targetDict, powerUpDict = categorizeRotation(targetDict, powerUpDict)
    targetDict, powerUpDict = catizgorizeProximityToOther(targetDict, powerUpDict)
    powerUpDict = categorizePowerupUsefulness(powerUpDict)
    targetDict = categorizeAmmo(targetDict)

    mergedDicts = targetDict + powerUpDict
    if (len(mergedDicts) != 0):
        bests = findBest(mergedDicts, 1)
        for entry in bests:
            if (entry["type"] == "target"):
                shootEnemy(entry["target"])
            elif (entry["type"] == "powerUp"):
                diff = diffVec2(ship.pos, entry["powerUp"].pos)
                ang = calcAng(diff, ship.calcAng)
                moveTo(diff, ang)
 
    
    pass

####################################################################################################
############################## DO NOT MODIFY  METHODS BELOW THIS LINE ##############################
########################## EXCEPT TO REMOVE TUTORIAL GAME CONFIG ARGUMENT  #########################
####################################################################################################
WindowArena(userCode1 = updateShipLiam,
            gameConfig = WindowArenaConfig.SPACE_BATTLE,
            windowTitle = "TSA@RHS: Space Battle!").runGameLoop()