# Hunt The Wumpus!

Top scores get Brookstone Rhapsody Bluetooth Headphones

Participants get a Box branded coffee mug. (Must average 4000 on 100 runs on 3 maps)

# Play a game
Download and run wumpus_ui.py (you will also need to download standard.txt to get the standard map). This will let you play the classic game on the standard map. Here are the instructions taken from the BASIC source code. The original BASIC source code is also in the repo if you want to take a look (It's amazing how small it is!)

       WELCOME TO 'HUNT THE WUMPUS'

        THE WUMPUS LIVES IN A CAVE OF 20 ROOMS: EACH ROOM HAS 3 TUNNELS LEADING TO OTHER
        ROOMS. THE STANDARD MAP IS A DODECAHEDRON (IF YOU DON'T KNOW WHAT A
        DODECAHEDRON IS, ASK SOMEONE)

        ***
        HAZARDS:

        BOTTOMLESS PITS - TWO ROOMS HAVE BOTTOMLESS PITS IN THEM
        IF YOU GO THERE: YOU FALL INTO THE PIT (& LOSE!)

        SUPER BATS  - TWO OTHER ROOMS HAVE SUPER BATS. IF YOU GO THERE, A BAT GRABS YOU
        AND TAKES YOU TO SOME OTHER ROOM AT RANDOM. (WHICH MIGHT BE TROUBLESOME)

        WUMPUS:

        THE WUMPUS IS NOT BOTHERED BY THE HAZARDS (HE HAS SUCKER FEET AND IS TOO BIG FOR
        A BAT TO LIFT). USUALLY HE IS ASLEEP. TWO THINGS WAKE HIM UP: YOUR ENTERING HIS
        ROOM OR YOUR SHOOTING AN ARROW.

            IF THE WUMPUS WAKES, HE EATS YOU IF YOU ARE THERE, OTHERWISE, HE MOVES (P=0.75)
        ONE ROOM OR STAYS STILL (P=0.25). AFTER THAT, IF HE IS WHERE YOU ARE, HE EATS
        YOU UP (& YOU LOSE!)


        YOU:

        EACH TURN YOU MAY MOVE OR SHOOT A CROOKED ARROW
        MOVING: YOU CAN GO ONE ROOM (THRU ONE TUNNEL)
        ARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN OUT.

            EACH ARROW CAN GO FROM 1 TO 5 ROOMS: YOU AIM BY TELLING THE COMPUTER THE ROOMS
        YOU WANT THE ARROW TO GO TO. IF THE ARROW CAN'T GO THAT WAY (IE NO TUNNEL) IT
        MOVES AT RANDOM TO THE NEXT ROOM.

            IF THE ARROW HITS THE WUMPUS: YOU WIN.

            IF THE ARROW HITS YOU: YOU LOSE.

            WARNINGS:

        WHEN YOU ARE ONE ROOM AWAY FROM WUMPUS OR HAZARD, THE COMPUTER SAYS:

        WUMPUS - 'I SMELL A WUMPUS'

        BAT - 'I HEAR BATS'

        PIT - 'I FEEL A DRAFT'

The wumpus game has been modified a little bit from the original for this contest, perhaps the most visible difference is the addition of a score. Getting killed results in a score of 0, while winning results in a score of 100 minus the number of moves taken. Shooting is free. If you shoot the wumpus without moving from your starting location you will get a score of 100.

# Time to bring in the computer!
After you have played a game or two yourself, you're ready to write your own wumpus hunting program. Open up wumpus_ai.py and take a look at status_callback() which tells you about your current situation and perform_move and perform_shoot which are the two actions you can take. The wumpus_ui.py file is similar but asks the user to input the decisions.

# Wait, is it already working?
The existing wumpus_ai.py file already works - it uses random to make the decisions. It also plays 100 games so you can see how well it performs on average: about 2,500 out of a possible 10,000
