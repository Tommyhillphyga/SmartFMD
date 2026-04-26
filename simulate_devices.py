from backend.scripts.simulate_devices import DeviceSimulator, parse_args


if __name__ == "__main__":
    args = parse_args()
    DeviceSimulator(args.host, args.port, args.interval).run()
