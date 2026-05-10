# Postman Collection Guide

## What is a Postman Collection?

A **Postman Collection** is a JSON file that contains a organized set of API requests. Think of it as a "saved favorites" for your API calls, but with descriptions, organization, and team sharing.

### Benefits:
- ✅ **Save requests** — Don't type URLs every time
- ✅ **Organize by folder** — Group related requests
- ✅ **Add descriptions** — Document each request
- ✅ **Share with team** — Send collection to collaborators
- ✅ **Reuse examples** — Quick demo scenarios
- ✅ **Variable support** — Use `{{base_url}}` etc.

---

## How to Use the Fuel Route Optimizer Collection

### 1. **Import the Collection into Postman**

#### Option A: Import from File
1. Open **Postman** on your machine
2. Click **"File"** → **"Import"**
3. Select **"postman_collection.json"** from the project root
4. Click **"Import"**

#### Option B: Copy the JSON Directly
1. Open Postman
2. Click **"+" → "Import"**
3. Paste the contents of `postman_collection.json`
4. Click **"Import"**

---

### 2. **Collection Structure**

Your collection is organized into 2 sections:

```
📁 Fuel Route Optimizer API
├── 📁 Demo Requests (4 examples)
│   ├── Dallas → Phoenix (Long Route)
│   ├── New York → Miami (Medium Route)
│   ├── San Francisco → Las Vegas (Short Route)
│   └── Chicago → Denver (Mountain Route)
└── 📁 Health & Status
    └── Health Check
```

---

### 3. **Using the Requests**

#### To Execute a Request:
1. Click on a request name (e.g., **"Dallas → Phoenix"**)
2. Review the request details:
   - **Method:** POST
   - **URL:** http://127.0.0.1:8000/api/v1/optimize-route/
   - **Body:** JSON with `start` and `destination`
3. Click **"Send"**
4. View the response in the lower panel

#### Example Response:
```json
{
  "success": true,
  "route": {
    "distance_m": 1234567,
    "duration_s": 18000,
    "waypoints": [...]
  },
  "optimization": {
    "total_cost": 247.50,
    "total_gallons_purchased": 20.5,
    "selected_stops": [
      {
        "id": 42,
        "name": "Shell Station",
        "coordinates": [33.123, -97.456],
        "gallons_to_purchase": 10.5,
        "distance_from_start_m": 250000
      }
    ],
    "candidate_count": 47
  }
}
```

---

### 4. **Demo Scenarios Explained**

#### **Dallas → Phoenix** (Primary Demo)
- **Distance:** ~1,000 miles
- **Expected stops:** 2-3 fuel stations
- **Demonstrates:** Multi-stop optimization
- **When to use:** Main demo, shows algorithm working

#### **New York → Miami**
- **Distance:** ~1,300 miles  
- **Expected stops:** 3-4 fuel stations
- **Demonstrates:** Long-distance efficiency
- **When to use:** Alternate scenario, different region

#### **San Francisco → Las Vegas**
- **Distance:** ~570 miles
- **Expected stops:** 0-1 fuel stations
- **Demonstrates:** Short route handling
- **When to use:** Show edge case, different algorithm behavior

#### **Chicago → Denver**
- **Distance:** ~920 miles
- **Expected stops:** 2 fuel stations
- **Demonstrates:** Midwest route optimization
- **When to use:** Regional diversity

---

### 5. **Using Variables (Advanced)**

You can make the collection more flexible with variables:

#### Set a Base URL Variable:
1. Click **"Fuel Route Optimizer API"** collection name
2. Go to **"Variables"** tab
3. Add variable:
   ```
   base_url: http://127.0.0.1:8000
   ```

#### Use It in Requests:
Instead of hardcoding `http://127.0.0.1:8000`, use:
```
{{base_url}}/api/v1/optimize-route/
```

This way, changing the base URL updates all requests.

---

### 6. **For Team Sharing**

#### Export the Collection:
1. Right-click collection name
2. Select **"Export"**
3. Choose JSON format
4. Save and share

#### Team Member Imports:
They follow the **"Import the Collection"** steps above.

---

### 7. **For Loom Recording**

When recording your demo:

1. **Open Postman** with the collection already imported
2. **Click on "Dallas → Phoenix"** request (main demo)
3. **Show the request body** — narrate what start/destination are
4. **Click "Send"** — let it execute
5. **Expand the response** — show key fields:
   - `total_cost`
   - `total_gallons_purchased`
   - `selected_stops` array
6. **Optionally try another request** (e.g., San Francisco → Las Vegas) to show variety

---

### 8. **Response Format Reference**

Every optimize-route response includes:

| Field | Description |
|-------|-------------|
| `success` | Boolean — request succeeded |
| `route.distance_m` | Route distance in meters |
| `route.duration_s` | Estimated duration in seconds |
| `optimization.total_cost` | Total fuel cost in USD |
| `optimization.total_gallons_purchased` | Gallons needed (10 mpg assumed) |
| `optimization.selected_stops` | Array of fuel stations to stop at |
| `optimization.candidate_count` | How many stations were evaluated |

---

### 9. **Troubleshooting**

| Issue | Solution |
|-------|----------|
| "Connection refused" | Ensure Django server is running: `python manage.py runserver` |
| "404 Not Found" | Check URL is correct and Django server is on port 8000 |
| "Empty response" | Make sure `ORS_API_KEY` is set (if using real API) |
| "CORS error" | Django CORS headers are configured in settings |

---

### 10. **Pro Tips**

- ✅ **Keep it updated** — Update collection when API changes
- ✅ **Use descriptions** — Help team understand each request
- ✅ **Test before demo** — Run requests once before recording
- ✅ **Save responses** — Click "Save Response" to document examples
- ✅ **Share versioned** — Keep collection.json in git (you already do!)

---

## How Collections Fit Into Your Workflow

```
1. Developer writes API
   ↓
2. Creates Postman collection with examples
   ↓
3. Tests requests locally
   ↓
4. Shares collection with team
   ↓
5. Records Loom demo using collection
   ↓
6. Evaluators import collection and test themselves
```

Your collection is now ready for all these steps! 🚀

---
