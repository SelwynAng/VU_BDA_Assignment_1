# Assignment 1

## GPS Spoofing Detection with Parallel Computing

### Goal

Analyze vessel tracking data from AIS records using parallel processing techniques to detect GPS spoofing events. Students will focus on efficient data handling, transformation, and performance evaluation using Python's parallel computing capabilities.

### Dataset

Students will use vessel tracking data from AIS Data: [AIS Data](http://web.ais.dk/aisdata/).  
Each student must select a single day’s data for analysis.  
Each student should pick a different day to avoid overlapping analysis.  
Coordinate your chosen date in the chat to ensure unique selections.

### Tasks

1. **Parallel Splitting of the Task**

   - **Objective:** Strategize the division of AIS data processing into parallelizable sub-tasks.
   - **Guidance:** Discuss different parallel computing techniques, such as data parallelism or task parallelism. Ensure workload balancing among parallel tasks.

2. **Implementation of Parallel Processing**

   - **Objective:** Develop Python code to process the AIS data in parallel for efficient computation.
   - **Guidance:** Utilize Python libraries for parallel processing.

3. **GPS Spoofing Detection**

   - **Objective:** Detect GPS spoofing events.
   - **Guidance:**
     - **Identifying Location Anomalies:** Detect sudden, unrealistic location jumps that deviate significantly from expected vessel movement patterns.
     - **Analyzing Speed and Course Consistency:** Identify vessels with inconsistent speed changes or impossible travel distances within a short time.
     - **Comparing Neighboring Vessel Data:** Check if multiple vessels in the same region report conflicting GPS positions.

4. **Evaluating Parallel Processing Efficiency**

   - **Objective:** Measure and evaluate the performance efficiency of parallelized processing techniques.
   - **Guidance:**
     - Compare execution time between sequential and parallel implementations.
     - Use speedup analysis: \( \text{Speedup} = \frac{\text{Time (sequential)}}{\text{Time (parallel)}} \)
     - Analyze CPU and memory usage across different numbers of parallel workers.
     - Test different numbers of CPUs and chunk sizes and compare their impact on execution time.
     - Visualize results in a graph showing performance improvements across configurations.
     - **Bonus (+1 point):** Students who execute their code on the Vilnius University HPC system and document their experience will receive an additional +1 grade to their task score.

5. **Presentation of the Solution**
   - **Objective:** Effectively present the solution to the GPS spoofing detection task.
   - **Guidance:** Clearly explain the implemented techniques, performance improvements, and findings in a structured manner.

### Submission and Presentation

- **Deadline:** All tasks (1-4) must be completed and submitted by the specified end date and time.
- **Presentation Format:** Up to 5 slides covering solutions to tasks 1-4.
- **Selection for Presentation:** One student from each group will be randomly chosen to present.
- **Requirement:** Students must submit their code to a specified code repository (GitHub, GitLab).

### Evaluation Criteria

- **Code Quality:** Clarity, efficiency, and correctness of the implementation.
- **GPS Spoofing Detection:** Accuracy and effectiveness in detecting spoofing events.
- **Performance Analysis:** Depth of parallel processing efficiency evaluation, speedup calculations, and visualization of results.
- **Use of Vilnius University HPC (+1 Point):** Proper execution and documentation of results on the HPC system.
- **Presentation:** Clarity and conciseness in explaining the solution.

## Steps to run program

### Setting up environment and running the code

1. Run `git clone https://github.com/SelwynAng/VU_BDA_Assignment_1.git`.
2. Use Anaconda to create a new environment by running `conda env -f environment.yml -n {new_env_name}`.
3. Run `conda activate {new_env_name}` to enter the newly created environment.
4. Download relevant dataset from http://web.ais.dk/aisdata/ and unzip the zip file to obtain CSV file. Store the CSV file under the `data/` directory.
5. Run `python3 main.py` and wait for the results in the CSV file and the plotted graph!
6. Note that you can toggle the chunk sizes and the number of workers in `main.py`.

### Running in Vilnius University's HPC

1. SSH into remote server via the command `ssh {VU_MIF_Username}@uosis.mif.vu.lt`, and it will prompt for password.
2. Once the remote server is accessed, SSH into HPC server via the command `ssh hpc`.
3. Copy the folder from local environment into remote server's environment first and then do the same from remote server to HPC's server via `scp` commands.
4. Remember to use Anaconda to create a new environment using `conda env create -f environment.yml -n {new_env_name}` and activate it via `conda activate {new_env_name}`.
5. Run `sbatch job.sh` to send the job to HPC and wait for results in the output text file.
6. Status of job can be viewed via the command `squeue`. Job can be cancelled using `scancel {job_id}` command too.
