### How to generate run_id

Goals:

1. Universally unique with low probability of collision
2. Short
3. Sorted by timestamp
4. Distributed uniformly, and easy to scale

Here are some options:

- **UUID**: Satisfies 1. and 3. (depend on version, e.g. UUID v7), and 4. but not 2. (could take up to 128 bits)
- **counter**: Satisifies 1., 2., 3. but not 4.
- **[TSID](https://www.foxhound.systems/blog/time-sorted-unique-identifiers/)**: good

### Demo


- Fix IMU query in the backend to match the count by downsampling
