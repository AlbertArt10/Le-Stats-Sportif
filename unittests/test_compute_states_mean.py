from app import webserver

# Test: Verificăm că se calculează corect mediile per stat pentru o întrebare dată.
def main():
    ingestor = webserver.data_ingestor
    question = "Percent of adults who engage in no leisure-time physical activity"
    print("Computed means for question:", question)
    means = ingestor.compute_states_mean(question)
    for state, mean in means.items():
        print(f"{state}: {mean}")

if __name__ == "__main__":
    main()
