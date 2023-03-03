# microchannel-cooling/api

## Usage

1. Build the Docker container: `make build`
2. Run the Docker container: `make run`
3. Test the API: `./example_post.sh`
4. Stop the Docker container: `make stop`

### Example

When you run `example_post.sh`, you should get the following response.

```
$ ./example_post.sh
{
  "input": {
    "L": 0.1,
    "W": 0.0001,
    "D": 1e-05,
    "T_in": 293,
    "T_w": 373,
    "Q": 100
  },
  "q": 188.65927945610323,
  "dP": 3794.0316374399995,
  "T_out": 47.10754954260585
}
```