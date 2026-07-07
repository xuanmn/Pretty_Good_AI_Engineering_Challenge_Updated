# Bug Report for each call session
1. For the first call it was going well but it seems like when transfering to a representative, it just ended the call. I messed up in the coding so I was not able to record the MP3 file for this call but fixed it afterwards moving forward.
2. Samething happened with the second call the call was ended after the bot gave DOB
3. Same issue as the second call.
4. Same issue as second call.
5. I changed the system prompt to test for a medication refill and the agent ended the call after giving DOB.
6. I changed the system prompt to canceling appointment and the agent ended the call after giving DOB.
7. I did another test with canceling and the agent ended the call after getting DOB.
8. It seems the agent keeps ending the call after getting the DOB. 
9. I changed the DOB on the system prompt and it still keeps ending the call after DOB.
10. Changed the system prompt by giving it the first name (Jamie Smith DOB March 12, 1990) and it got deeper into the conversation and the agent connected with a representive.
11. I switched to the cancel appointment prompt with the name (Jamie Smith DOB March 12, 1990) and it was able to successfully cancel the appointment.
12. Ran the test with general question asking about insurance, hours, and location and It was able to get all of the information.
14. Ran the canceling appointment and noticed it made me go through the loop of repeating DOB and Name. It did get through to the end sucessfully sort of because it was off hours the agent couldnt fully canceled and It would have to try again is what iam thinking.
15. Some issues with transcription not capturing the correct words on both end the agent and the AI. I also noticed when asked a phone number it made up a number which is understandable since i did not put the number in the system prompt.


# Conclusion
Based on these test calls the it the call agent tries to match the phone number with the inital name and DOB. If you change the system prompt to give another name and DOB but do not change the phone number the agent will just hang up the call randomly. So intintally I had Jamie Smith DOB March 12, 1990 and making this call under these name connected me to what I wanted but after changing the prompt to Alex DOB July 4 2000 the agent will just end the call after the bot tells the DOB. It seems like the bot needs to be the same person with the same DOB and information that it's trying to simulate. 