from bson import ObjectId

dummy_data = {
    "ocean": [
        {
            # id is the same as owner's id
            "_id": ObjectId("603f5b40872f4f94a26d027e"),
            "known_faces": {
                "imranKhan": {
                    "name": ["Imran Khan"]
                },
                "shahrukh": {
                    "name": ["Shahrukh Khan"]
                },
            },
            "buckets": [
                {
                    "name": "bucketone",
                    "items": [
                        {"path": "/", "title": "buildings.jpg"},
                        {"path": "/", "title": "car.jpg"},
                        {"path": "/", "title": "cats.jpg"},
                        {"path": "/", "title": "cups.jpg"},
                    ],
                }
            ],
        }
    ]
}
