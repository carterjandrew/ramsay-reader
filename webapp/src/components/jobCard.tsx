import { Box, Center, Text } from '@chakra-ui/react'
import { Job } from '../App'
import { useEffect, useState } from 'react'

export type ResultCardProps = {
	job: Job,
}

const ResultCard: React.FC<ResultCardProps> = ({ job }) => {
	return (
		<Center
			flexDir='column'
			bg='white'
			gap={2}
			padding={5}
			shadow='2xl'
			shadowColor='fg'
			fontSize={23}
			borderRadius={20}
			border='solid'
			borderWidth={1}
			borderColor='gray.200'
			zIndex={2}
			maxW='100%'
		>
			<Text>{job.text}</Text>
			<audio controls>
				<source
					src={`http://localhost:5000/result/${job.id}`}
					type='audio/wav'
				/>
				Your browser does not support audio
			</audio>
		</Center>
	)
}

export default ResultCard
