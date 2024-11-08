This is very incomplete, but follows the general form:
  - Near stateless frontend
  - Data all managed in session_manager, to facilitate easy transfer to it being stored in external/persistent methods later on
  - Neetocal and openai as separate managers, to allow swapping of apis used

Script used for testing:
-I recently gave birth and am really out of shape. I saw an ad on Instagram for your personal training offer
- sure
- i just want to get stronger and repair my ab separation
- great

Notes:
- the actual selection of the appointment time isn't working for now -- I'd need to implement a little state management to allow confirmation of the selection
- I did not use any RAG or reference the provided informational page. I don't have time, and I think it would add pretty little value over the current openai model. I tested the openai model and it seems to already have most of that information.
- I did almost no testing of other scripts -- I'm sure there are a million things that would break it, and tons of potentially harmful edge cases (for instance, the ai is willing to present itself as a medical professional)
