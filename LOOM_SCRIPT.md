# Fuel Route Optimizer – 5-Minute Loom Recording Script

**Total Duration:** 5 minutes (300 seconds)  
**Format:** Screen recording with voiceover narration

---

## **PART 1: INTRODUCTION & SETUP (0:00 – 0:15)**

### 0:00 – 0:03
**ACTION:** Start screen recording. Show desktop. Click to open Postman.  
**NARRATION:**  
*"Hi, I'm Aradhya. This is the Fuel Route Optimizer API—a Django backend that finds the most cost-effective route and optimal fuel stops between two US locations. Let me show you how it works."*

### 0:03 – 0:08
**ACTION:** Wait for Postman to load. Maximize window.  
**NARRATION:**  
*"I've built this with Django, integrated with the OpenRouteService API for routing, and a custom algorithm to find the cheapest fuel stops along the way. The vehicle has a 500-mile range, so we may need multiple fuel stops."*

### 0:08 – 0:15
**ACTION:** Click on the "Optimize Route" request in Postman collection.  
**NARRATION:**  
*"Let me demo this with a real request from Dallas, TX to Phoenix, AZ—about 1,000 miles. The API will show the route, all optimal fuel stops, and the total cost."*

---

## **PART 2: POSTMAN DEMO – REQUEST SETUP (0:15 – 0:45)**

### 0:15 – 0:20
**ACTION:** Show the request details in Postman. Highlight the URL bar.  
**NARRATION:**  
*"This is our endpoint: POST /api/v1/optimize-route/. It accepts a JSON body with a start and destination location."*

### 0:20 – 0:28
**ACTION:** Scroll to the "Body" tab. Show the JSON request.  
**NARRATION:**  
*"The request is simple: start and destination. Both are text locations—addresses or city names. Behind the scenes, we geocode these to coordinates, fetch the route from OpenRouteService in a single API call, then run our optimization algorithm to find the best fuel stops."*

### 0:28 – 0:35
**ACTION:** Point at the body JSON. Hover over it with cursor.  
**NARRATION:**  
*"We're sending Dallas, TX to Phoenix, AZ. That's roughly 1,000 miles. With a 500-mile max range, we'll definitely see multiple fuel stops in the response."*

### 0:35 – 0:45
**ACTION:** Prepare to hit Send. Make sure Django server is running in background (or have it ready). Point to the "Send" button.  
**NARRATION:**  
*"I'm using actual fuel station prices from the dataset provided. The algorithm picks stops that minimize total fuel cost while respecting the vehicle's range constraint. Let me send this request and show you the response."*

---

## **PART 3: POSTMAN DEMO – EXECUTION & RESPONSE (0:45 – 2:30)**

### 0:45 – 0:50
**ACTION:** Click "Send" button. Wait for response (2–3 seconds). Postman shows the response JSON.  
**NARRATION:**  
*"Sending... and the API responds quickly. You can see the full JSON response with all the route details and optimization results."*

### 0:50 – 1:10
**ACTION:** Scroll through the response JSON. Point to key fields:
- `"success": true`
- `"route"` object
- `"optimization"` object  

**NARRATION:**  
*"The response includes success status, the full route details, and our optimization result. Let me break down what's in each section. First, the route object contains the full path from start to destination."*

### 1:10 – 1:35
**ACTION:** Expand the `"optimization"` object in the JSON. Highlight:
- `"total_cost"`
- `"total_gallons_purchased"`
- `"selected_stops"` (array of fuel stations)
- `"candidate_count"`  

**NARRATION:**  
*"Here's the optimization result. Total cost is the amount the driver will spend on fuel for the entire trip. Total gallons purchased assumes 10 miles per gallon. The selected_stops array contains each fuel station we recommend, with coordinates and the amount to fuel up at each stop."*

### 1:35 – 2:00
**ACTION:** Click into one of the `selected_stops` entries. Show:
- Coordinates
- Amount to purchase
- Distance from start  

**NARRATION:**  
*"Each stop includes GPS coordinates so you can plot them on a map, the amount of fuel to buy (in gallons), and the distance from the start. Our algorithm picked this stop because it's cost-effective and keeps us within the 500-mile range before we run out of gas."*

### 2:00 – 2:15
**ACTION:** Scroll to the end of the response. Show `"candidate_count"`.  
**NARRATION:**  
*"The candidate count tells us how many potential fuel stations the algorithm evaluated. Even though there are many candidates, we efficiently filtered down to just the most cost-effective ones."*

### 2:15 – 2:30
**ACTION:** Minimize Postman. Get ready to show code.  
**NARRATION:**  
*"Now let me quickly show you the code behind this. The architecture is clean and efficient—one API call to get the route, then a custom optimization algorithm."*

---

## **PART 4: CODE OVERVIEW – MAIN ENTRY POINT (2:30 – 3:00)**

### 2:30 – 2:35
**ACTION:** Open VS Code. Navigate to `fuel_optimizer/apps/route_optimizer/api/v1/views/optimization_view.py`.  
**NARRATION:**  
*"This is the main API view. It orchestrates the entire workflow: validate the request, fetch the route, optimize for fuel costs, and return the response."*

### 2:35 – 2:50
**ACTION:** Highlight the `post()` method. Point to these lines:
- Line 38: `provider = OpenRouteServiceProvider()`
- Line 39: `routing = RoutingService(provider)`
- Line 42: `route_summary = routing.get_route(start, destination)`  

**NARRATION:**  
*"Here's where we make the routing API call—just one call. We create a provider (OpenRouteService), wrap it in a RoutingService, and call get_route. This returns the full route including distance, duration, and waypoints."*

### 2:50 – 3:00
**ACTION:** Scroll down. Point to:
- Line 47: `optimizer = FuelOptimizationService()`
- Line 49: `optimization = optimizer.optimize(route_summary)`  

**NARRATION:**  
*"Then we instantiate the fuel optimization service and run the algorithm. The algorithm takes the route and returns the optimal fuel stops that minimize cost."*

---

## **PART 5: CODE OVERVIEW – OPTIMIZATION LOGIC (3:00 – 3:45)**

### 3:00 – 3:10
**ACTION:** Open `fuel_optimizer/apps/route_optimizer/services/fuel_optimization_service.py`.  
**NARRATION:**  
*"This is where the magic happens—the fuel optimization algorithm. It considers three main constraints: vehicle range (500 miles), fuel prices at different stations, and total distance."*

### 3:10 – 3:25
**ACTION:** Scroll to the `optimize()` method. Highlight key logic:
- Iterates through the route
- Finds fuel stations within range
- Scores each station by cost
- Selects the cheapest options  

**NARRATION:**  
*"The algorithm walks along the route segment by segment. At each position, it finds all fuel stations we can reach within our 500-mile range. It then scores each candidate by the cost per gallon and selects the cheapest option. This is greedy but optimal for our use case."*

### 3:25 – 3:40
**ACTION:** Point to the return statement showing `OptimizationResult`.  
**NARRATION:**  
*"The result is an OptimizationResult object that includes total cost, total gallons, the list of selected stops with their coordinates, and metadata. Everything the frontend needs to display the map and guide the driver."*

### 3:40 – 3:45
**ACTION:** Click into `domain/optimization_models.py` to quickly show the data structure.  
**NARRATION:**  
*"Here are the data models—clean and typed with Python dataclasses. Easy to serialize to JSON and return to the client."*

---

## **PART 6: CODE OVERVIEW – INFRASTRUCTURE & PERFORMANCE (3:45 – 4:30)**

### 3:45 – 3:55
**ACTION:** Open `fuel_optimizer/apps/route_optimizer/infrastructure/routing/ors_provider.py`.  
**NARRATION:**  
*"This is the OpenRouteService provider. It wraps the external routing API. We're careful to make only one call and cache the results where possible to keep response times fast."*

### 3:55 – 4:10
**ACTION:** Point to the `get_route()` method. Highlight:
- URL construction
- Timeout handling
- Error handling  

**NARRATION:**  
*"The provider handles geocoding text addresses to coordinates, calls the ORS API with the correct profile (driving-car), and returns a detailed route. The timeout is set to 10 seconds, so the entire API response is usually under 1-2 seconds."*

### 4:10 – 4:20
**ACTION:** Quickly show `repositories/fuel_station_repository.py`.  
**NARRATION:**  
*"We also have a repository layer that queries the fuel station database. This is how we know the prices and locations of all candidate stops. The data comes from the CSV file provided."*

### 4:20 – 4:30
**ACTION:** Show the test file `tests/test_api_smoke.py`.  
**NARRATION:**  
*"We have comprehensive tests. The smoke test mocks the routing and optimization services to validate the API contract without external dependencies. All tests pass in CI."*

---

## **PART 7: CLOSING & NEXT STEPS (4:30 – 5:00)**

### 4:30 – 4:45
**ACTION:** Switch back to terminal. Show git commits with `git log --oneline -5`.  
**NARRATION:**  
*"The code is version controlled and ready for production. Recent commits include CI/CD fixes to ensure the tests run smoothly. The entire codebase is on GitHub for your review."*

### 4:45 – 4:55
**ACTION:** Show the README.md (or quickly summarize setup steps verbally).  
**NARRATION:**  
*"To run this locally: clone the repo, install dependencies from requirements/dev.txt, run migrations, and start the Django server. The API is immediately available at /api/v1/optimize-route/. Everything is documented in the README."*

### 4:55 – 5:00
**ACTION:** End screen recording. Smile at camera briefly if visible.  
**NARRATION:**  
*"That's the Fuel Route Optimizer API. It's fast, efficient with external API calls, and solves the real problem of finding cost-effective fuel stops on long routes. Thanks for watching, and let me know if you have any questions!"*

---

## **TIMING CHECKLIST**

- [ ] **0:00 – 0:15** — Intro (15 sec)
- [ ] **0:15 – 0:45** — Postman Setup (30 sec)
- [ ] **0:45 – 2:30** — API Demo & Response Walkthrough (105 sec)
- [ ] **2:30 – 3:00** — Main View Code (30 sec)
- [ ] **3:00 – 3:45** — Optimization Service (45 sec)
- [ ] **3:45 – 4:30** — Infrastructure & Tests (45 sec)
- [ ] **4:30 – 5:00** — Closing & Setup (30 sec)

**Total: 300 seconds (5 minutes)**

---

## **TIPS FOR RECORDING**

1. **Practice once silently** to get timing right.
2. **Speak clearly and slowly**—assume the audience isn't a developer.
3. **Use cursor/highlighting** to draw attention to important lines.
4. **Pause for 1-2 seconds** after each major action so viewers can read.
5. **Record at 1080p** if possible for code readability.
6. **Have the Django server running** before you start (or mock the response).
7. **Test the Postman request** once before recording to ensure it works.
8. **Keep narration natural**—don't rush. Better to be at 4:50 than to finish at 3:00.

---

## **KEY TALKING POINTS (Memorize These)**

- ✅ *"One API call to OpenRouteService, minimal external dependencies"*
- ✅ *"Response time: typically <2 seconds"*
- ✅ *"Algorithm considers 500-mile range and fuel prices"*
- ✅ *"Clean, typed Python code with comprehensive tests"*
- ✅ *"Django best practices: views, services, repositories, domain models"*

---
