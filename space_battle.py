from lib.window_arena import *
from lib.winobj_ship import *
from typing import List

# update ship (this is where your code goes)
def updateShip1(ship: Ship, powerUps: List[PowerUp], targets: List[Target]):

    ship.setPlayerName("Liam C")

    shipAmmoSpeed = Ammo.SPEED #(units per second)
    shipAmmoDistance = ship.ammoMaxRange # (units)
    shipRotationSpeed = ship.shipTurnSpeed # (degrees per second)
    shipMoveSpeed = ship.shipMoveSpeed # (units per second)

    ship.DEFAULT_MOVE_SPEED
    
    enoughAmmo = 5 # more than this = shoot

    shipRad = math.atan2(ship.dir[1], ship.dir[0])
    shipAng = math.degrees(shipRad)

    #finds distance between two x and y differences
    def distance(diff):
        return math.sqrt(math.pow(diff[0], 2) + math.pow(diff[1], 2))
    
    def normalizeVec2(vector2, normalizeVal):
        vector2[0] = vector2[0] / normalizeVal
        vector2[1] = vector2[1] / normalizeVal
        return vector2

    def diffVec2(startPos, endPos):
        xDiff = endPos[0] - startPos[0]
        yDiff = endPos[1] - startPos[1]
        return [xDiff, yDiff]

    def calcAng(diff, startAng):

        inputRad = math.atan2(diff[1], diff[0])
        outputAng = startAng - math.degrees(inputRad)

        possBetterAng1 = (outputAng - 360)
        possBetterAng2 = (outputAng + 360)

        if abs(possBetterAng1) < abs(outputAng):
            outputAng = possBetterAng1
        if abs(possBetterAng2) < abs(outputAng):
            outputAng = possBetterAng2

        return outputAng

    # assumes you use the best path
    def predictTimeSec(distance, startAng, endAng):
        outputTime = 0
        
        # ship rot time
        outputTime += abs(endAng - startAng) / shipRotationSpeed

        # ship move time (dont count if the distance is less 0 since your not mvoing then)
        moveDistance = (distance - shipAmmoDistance)
        if (moveDistance > 0):
            outputTime += moveDistance / shipMoveSpeed

        # ammo move time
        outputTime += shipAmmoDistance / shipAmmoSpeed

        return outputTime

    def predictTarget(target, time):
        #Predicts where target will be after a certain amount of time
        #And finds the closest position the ship needs to move to in order to shoot the target 
        #Based on shipAmmoDistance and shipAmmoSpeed
        predictedXPos = target.pos[0] + (target.vel[0] * time)
        predictedYPos = target.pos[1] + (target.vel[1] * time)

        predictedCoords = [predictedXPos, predictedYPos]
        predictedDiff = diffVec2(ship.pos, predictedCoords)
        distTargetPredicted = distance(predictedDiff)
        
        normalizedVector = normalizeVec2(predictedDiff, distTargetPredicted)
        circleX, circleY = predictedXPos, predictedYPos
        if (distTargetPredicted > shipAmmoDistance):
            circleX -= (normalizedVector[0] * shipAmmoDistance)
            circleY -= (normalizedVector[1] * shipAmmoDistance)

        outputVec = diffVec2(ship.pos, [circleX, circleY])
        outputAngle = calcAng(outputVec, shipAng)
        
        return outputVec, outputAngle, distTargetPredicted
        
    def moveTo(diff, angle):

        absoluteAng = abs(angle)

        dist = distance(diff)

        if angle > 0:
            ship.queueCommand( ShipCmd_ThrustLeft(absoluteAng))
        else:
            ship.queueCommand( ShipCmd_ThrustRight(absoluteAng))
        
        ship.queueCommand( ShipCmd_Thrust(dist) )

    def findClosest(startPos, targets):
        closest = None
        closestDist = math.inf

        for target in targets:
            
            diff = diffVec2(startPos, target.pos)
            
            dist = distance(diff)
            if dist < closestDist:
                closestDist = dist
                closest = target

        return closest

    def shootEnemies(startPos, targets):

        for target in targets:
            
            diff = diffVec2(startPos, target.pos)

            dist = distance(diff)

            targetAng = calcAng(diff, shipAng)

            predictedTime = predictTimeSec(dist, shipAng, targetAng)
            predictedVector, predictedAngle, predictedDist = predictTarget(target, predictedTime)
            
            if predictedDist > shipAmmoDistance:

                moveTo(predictedVector, predictedAngle)

            ship.queueCommand( ShipCmd_Shoot(normalizeVec2(predictedVector, predictedDist)))

    if ship.ammo > enoughAmmo:
        # shoot enemy loop
        shootEnemies(ship.pos, targets)
    else:
        # grab ammo loop
        closestTarget = findClosest(ship.pos, powerUps)

        if closestTarget != None:
            diff = diffVec2(ship.pos, closestTarget.pos)
            moveTo(diff, calcAng(diff, shipAng))
    
    pass
####################################################################################################
############################## DO NOT MODIFY  METHODS BELOW THIS LINE ##############################
########################## EXCEPT TO REMOVE TUTORIAL GAME CONFIG ARGUMENT  #########################
####################################################################################################
WindowArena(userCode1 = updateShip1,
            gameConfig = WindowArenaConfig.SPACE_BATTLE,
            windowTitle = "TSA@RHS: Space Battle!").runGameLoop()