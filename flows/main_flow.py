from metaflow import FlowSpec, step

class MainFlow(FlowSpec):

    @step
    def start(self):
        print("Start step")
        # Example: load data, initialize parameters
        self.data = []
        self.next(self.process)

    @step
    def process(self):
        print("Process step")
        # Example: simple transformation
        self.processed_data = [x*2 for x in self.data]
        self.next(self.end)

    @step
    def end(self):
        print("Flow complete")
        print("Processed data:", getattr(self, "processed_data", None))

if __name__ == "__main__":
    MainFlow()