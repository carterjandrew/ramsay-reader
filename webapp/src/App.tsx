import { Box, Button, Center, Flex, Heading, Image, Input, Slider, Spinner, Text, Textarea } from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { FaFastBackward, FaFastForward, FaGithub, FaPlay, FaPlayCircle } from "react-icons/fa"
import { LuChefHat } from "react-icons/lu"
import JobCard from "./components/jobCard"

export type Job = {
	text: string,
	status: {
		status: string,
		error?: string
	}
	id?: string,
}

export default function Page() {
	const [boxHeight, setBoxHeight] = useState<number>(0)
	const [inputText, setInputText] = useState('')
	const [job, setJob] = useState<Job>()
	const [results, setResults] = useState<Job[]>([])
	const intervalRef = useRef<number>(null)

	function handleBoxRef(ref: HTMLDivElement) {
		if (!ref) return
		setBoxHeight(ref.clientWidth)
	}

	useEffect(() => {
		console.log(job)
		async function handleJobChange() {
			if (!job) return
			if (job.status.status === 'creating') {
				const response = await fetch('http://localhost:5000/submit', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						text: job.text
					})
				})
				const id = (await response.json())[0].job_id
				setJob({
					...job,
					id: id,
					status: {
						status: 'queued'
					}
				})
			}
			if (job.status.status === 'completed') {
				setResults([
					...results,
					job
				])
				setJob(undefined)
			}
		}
		handleJobChange()
	}, [job])

	async function pollJobStatus() {
		if (!job || !job.id) return
		const response = await fetch(
			`http://localhost:5000/status/${job?.id}`
		)
		const status = (await response.json())
		setJob({
			...job,
			status: status
		})
	}

	useEffect(() => {
		if (job && job.status.status !== 'completed') {
			intervalRef.current = setInterval(pollJobStatus, 5000)
		} else {
			if (intervalRef.current) {
				clearInterval(intervalRef.current)
				intervalRef.current = null
			}
		}
		return () => {
			if (!intervalRef.current) return
			clearInterval(intervalRef.current)
			intervalRef.current = null
		}

	}, [job])

	function renderButton() {
		if (!job) return (
			<Button
				onClick={() => {
					if (inputText.length < 1 || inputText.length > 200) return
					setJob({
						status: {
							status: 'creating',
						},
						text: inputText
					})
				}}
			>
				<LuChefHat />
				Start Cooking
			</Button>
		)
		if (job.status.status !== 'completed') return (
			<Button >
				<Spinner />
				{job.status.status} request
			</Button >
		)
		if (job.status.status === 'completed') return (
			<Button >
				<Spinner />
				Job completed, downloading audio
			</Button >
		)
	}

	return (
		<Flex
			flexDir='column'
			w='100vw'
			h='100vh'
			minH={0}
			fontFamily=''
			background='gray.subtle'
		>
			<Flex
				flexDir='row'
				padding={3}
				fontSize='3xl'
			>
				<Flex flex={1} />
				<Flex flexDir='row'>
					<Text> The Ramsay Expirience </Text>
				</Flex>
				<Flex
					flex={1}
					flexDir='row'
					alignItems='center'
					justifyContent='end'
				>
					<FaGithub />
				</Flex>
			</Flex>
			<Flex
				flex={1}
				w='100%'
				flexDir='column'
				overflowY='scroll'
				alignItems='center'
			>
				<Box h='20vh' />
				<Image
					src='ramsay.png'
					objectFit='contain'
					zIndex={0}
					width={`${boxHeight}px`}
				/>
				<Center
					flexDir='column'
					gap={2}
					padding={5}
					shadow='2xl'
					shadowColor='fg'
					fontSize={23}
					borderRadius={20}
					border='solid'
					borderWidth={1}
					borderColor='gray.200'
					zIndex={1}
					bg='bg'
					ref={handleBoxRef}
				>
					<Textarea
						fontSize='xl'
						placeholder='What should Gordon say?'
						value={inputText}
						onChange={(e) => setInputText(e.target.value)}
						disabled={!!job}
					/>
					{renderButton()}
				</Center>
				<Flex
					flexDir='column'
					alignItems='center'
					padding={2}
					gap={2}
				>
					{results.map((result, index) => (
						<JobCard
							key={index}
							job={result}
						/>
					))}
				</Flex>
			</Flex>
		</Flex>
	)
}
